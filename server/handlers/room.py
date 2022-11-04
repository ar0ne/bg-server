"""Room handlers"""
from dataclasses import asdict
from datetime import datetime
from typing import Optional

from resources.errors import APIError
from tornado.escape import json_decode

from server.constants import GameRoomStatus
from server.resources.auth import login_required
from server.resources.handlers import BaseRequestHandler
from server.resources.models import Game, Room, RoomListSerializer, RoomSerializer


class GameRoomHandler(BaseRequestHandler):
    """Game room handler"""

    @login_required
    async def post(self, game_id: str) -> None:
        """Create game room"""
        game = await Game.get(id=game_id)
        admin = self.request.user
        room_size = self.request.arguments.get("size") or game.min_size
        room = await Room.create(
            admin=admin, game=game, status=GameRoomStatus.CREATED.value, size=room_size
        )
        await room.participants.add(admin)
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.set_status(201)
        self.write(serializer.json())


class RoomHandler(BaseRequestHandler):
    """Room request handler"""

    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            # FIXME: add limit
            # FIXME: filter open to join pages only
            serializer = await RoomListSerializer.from_queryset(Room.all())
            self.write(serializer.json())
        else:
            room = await Room.get(id=room_id).select_related("game")
            serializer = await RoomSerializer.from_tortoise_orm(room)
            response = {
                "room": json_decode(serializer.json()),
            }
            if room.status != GameRoomStatus.CREATED.value:
                engine = room.game.get_engine()(room_id)
                response["data"] = asdict(await engine.poll())
            self.write(response)

    @login_required
    async def put(self, room_id: str) -> None:
        """Player could make game turns"""
        current_user = self.request.user
        room = await Room.get(id=room_id).select_related("game")
        if current_user.id != room.admin_id:
            raise APIError(401, "Can't perform this action.")

        # FIXME: add validation
        data = self.request.arguments
        if "room_state" in data:
            new_state = data["room_state"]
            room.status = GameRoomStatus[new_state].value
            if new_state == GameRoomStatus.STARTED.name:
                players_ids = await room.participants.all().values_list("id", flat=True)
                # new game event triggered
                engine = room.game.get_engine()(room_id)
                await engine.setup(players_ids)

        if "size" in data:
            room.size = data["size"]
        await room.save(update_fields=("status", "size"))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.json())


class RoomPlayersHandler(BaseRequestHandler):
    """Room players handler"""

    @login_required
    async def post(self, room_id: str) -> None:
        """join room"""
        player_id = self.request.arguments.get("user_id")
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).prefetch_related("participants")
        player_already_joined = await room.participants.filter(id__in=player_id).exists()
        if not room or player_already_joined:
            raise APIError(400, "User already joined the room.")
        await room.participants.add(current_user)
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.json())

    @login_required
    async def delete(self, room_id: str, player_id: str) -> None:
        """Player could cancel own participation"""
        # TODO: dry it!
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).select_related("admin").prefetch_related("participants")
        is_admin = current_user.id is room.admin.id
        player_participate = any(filter(lambda p: p.id == current_user.id, room.participants))
        if not (room and player_participate):
            raise APIError(400, "User aren't participant of the room.")
        await room.participants.remove(current_user)
        if is_admin and not len(room.participants):
            # cancel room if there are no participants
            room.status = GameRoomStatus.CANCELED.value
            room.date_closed = datetime.now()
            await room.save(update_fields=("status",))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.json())
