import asyncio

import redis.asyncio as aioredis

from tornado.websocket import WebSocketClosedError


class RedisPubSubManager:
    """
        Initializes the RedisPubSubManager.

    Args:
        host (str): Redis server host.
        port (int): Redis server port.
    """

    def __init__(self, host: str, port: int) -> None:
        self.redis_host = host
        self.redis_port = port
        self.pubsub = None

    async def _get_redis_connection(self) -> aioredis.Redis:
        """
        Establishes a connection to Redis.

        Returns:
            aioredis.Redis: Redis connection object.
        """
        return aioredis.Redis(
            host=self.redis_host, port=self.redis_port, auto_close_connection_pool=False
        )

    async def connect(self) -> None:
        """
        Connects to the Redis server and initializes the pubsub client.
        """
        self.redis_connection = await self._get_redis_connection()
        self.pubsub = self.redis_connection.pubsub()

    async def _publish(self, room_id: str, message: str) -> None:
        """
        Publishes a message to a specific Redis channel.

        Args:
            room_id (str): Channel or room ID.
            message (str): Message to be published.
        """
        await self.redis_connection.publish(room_id, message)

    async def subscribe(self, room_id: str) -> aioredis.Redis:
        """
        Subscribes to a Redis channel.

        Args:
            room_id (str): Channel or room ID to subscribe to.

        Returns:
            aioredis.ChannelSubscribe: PubSub object for the subscribed channel.
        """
        await self.pubsub.subscribe(room_id)
        return self.pubsub

    async def unsubscribe(self, room_id: str) -> None:
        """
        Unsubscribes from a Redis channel.

        Args:
            room_id (str): Channel or room ID to unsubscribe from.
        """
        await self.pubsub.unsubscribe(room_id)


class WebSocketManager:
    """Websocket manager"""

    def __init__(self, pubsub_client) -> None:
        """
        Initializes the WebSocketManager.

        Attributes:
            rooms (dict): A dictionary to store WebSocket connections in different rooms.
            pubsub_client (RedisPubSubManager): An instance of the RedisPubSubManager class for pub-sub functionality.
        """
        self.rooms: dict = {}
        self.pubsub_client = pubsub_client

    async def add_user_to_room(self, room_id: str, websocket) -> None:
        """
        Adds a user's WebSocket connection to a room.

        Args:
            room_id (str): Room ID or channel name.
            websocket (WebSocket): WebSocket connection object.
        """
        if room_id in self.rooms:
            self.rooms[room_id].append(websocket)
        else:
            self.rooms[room_id] = [websocket]

            await self.pubsub_client.connect()
            pubsub_subscriber = await self.pubsub_client.subscribe(room_id)
            asyncio.create_task(self._pubsub_data_reader(pubsub_subscriber))

    async def broadcast_to_room(self, room_id: str, message: str) -> None:
        """
        Broadcasts a message to all connected WebSockets in a room.

        Args:
            room_id (str): Room ID or channel name.
            message (str): Message to be broadcasted.
        """
        await self.pubsub_client._publish(room_id, message)

    async def remove_user_from_room(self, room_id: str, websocket) -> None:
        """
        Removes a user's WebSocket connection from a room.

        Args:
            room_id (str): Room ID or channel name.
            websocket (WebSocket): WebSocket connection object.
        """
        if websocket not in self.rooms[room_id]:
            return
        self.rooms[room_id].remove(websocket)

    async def _cleanup_rooms(self) -> None:
        """Check if all rooms have alive connections, otherwise unsubscribe them"""
        for room_id in self.rooms:
            if not len(self.rooms[room_id]):
                del self.rooms[room_id]
                await self.pubsub_client.unsubscribe(room_id)

    async def _pubsub_data_reader(self, pubsub_subscriber):
        """
        Reads and broadcasts messages received from Redis PubSub.

        Args:
            pubsub_subscriber (aioredis.ChannelSubscribe): PubSub object for the subscribed channel.
        """
        while True:
            message = await pubsub_subscriber.get_message(ignore_subscribe_messages=True)
            if message is None:
                continue
            room_id = message["channel"].decode("utf-8")
            all_sockets = self.rooms[room_id]
            data = message["data"].decode("utf-8")
            removable = []
            for socket in all_sockets:
                try:
                    await socket.write_message(data)
                except WebSocketClosedError:
                    removable.append(socket)
            for socket in removable:
                await self.remove_user_from_room(room_id, socket)
            await self._cleanup_rooms()
