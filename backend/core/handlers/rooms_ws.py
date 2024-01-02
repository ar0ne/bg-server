"""Websocket handler"""
import logging

from tornado.websocket import WebSocketHandler

log = logging.getLogger(__name__)


class RoomWebSocketHandler(WebSocketHandler):
    """Room websocket handler"""

    def check_origin(self, origin):
        return True

    async def open(self, *args, **kwargs) -> None:
        self.set_nodelay(True)
        if not args:
            return
        if room_id := args[0]:
            await self.application.socket_manager.add_user_to_room(room_id, self.ws_connection)

    async def on_message(self, message: str | bytes) -> None:
        if message and message == "refresh" and self.open_args:
            if room_id := self.open_args[0]:
                await self.application.socket_manager.broadcast_to_room(room_id, message)
            return
        self.write_message(message)
