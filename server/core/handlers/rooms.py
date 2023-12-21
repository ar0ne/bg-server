"""Room handlers"""
from datetime import datetime
from typing import Optional

import tornado
from core.constants import GameRoomStatus
from core.loaders import get_engine
from core.resources.auth import login_required
from core.resources.errors import APIError
from core.resources.handlers import BaseRequestHandler
from core.resources.models import Game, Player, Room, RoomListSerializer, RoomSerializer
from core.types import Id
from tortoise.contrib.pydantic.base import PydanticListModel, PydanticModel


class GameRoomHandler(BaseRequestHandler):
    """
    Game room request handler.
    Allows to create new game room.
    """

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
        data = serializer.model_dump(mode="json")
        self.write(dict(data=data))


class RoomHandler(BaseRequestHandler):
    """
    Room request handler.
    Allows to get all available game rooms, room details, setup room (and start game).
    """

    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            # FIXME: add limit
            # FIXME: filter open to join pages only
            list_serializer: PydanticListModel = await RoomListSerializer.from_queryset(Room.all())
            rooms = list_serializer.model_dump(mode="json")
            self.write(dict(results=rooms))
        else:
            room = await Room.get(id=room_id).select_related("game")
            serializer: PydanticModel = await RoomSerializer.from_tortoise_orm(room)
            data = serializer.model_dump(mode="json")
            self.write(dict(data=data))

    @login_required
    async def put(self, room_id: str) -> None:
        """Player could setup game settings"""
        current_user = self.request.user
        room = await Room.get(id=room_id).select_related("game")
        if current_user.id != room.admin_id:  # type: ignore
            raise APIError(401, "Can't perform this action.")

        # FIXME: add validation
        data = self.request.arguments
        if "status" in data:
            status = data["status"]
            room.status = GameRoomStatus(status).value
            if status == GameRoomStatus.STARTED.value:
                players_ids = list(
                    map(str, await room.participants.all().values_list("id", flat=True))
                )
                # new game event triggered
                engine = get_engine(room)
                await engine.setup(players_ids)

        if "size" in data:
            if room.game.min_size < data["size"] > room.game.max_size:
                raise Exception  # FIXME: raise validation error
            room.size = data["size"]
        await room.save(update_fields=("status", "size"))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        data = serializer.model_dump(mode="json")
        self.write(dict(data=data))


class RoomDataHandler(BaseRequestHandler):
    """
    Game Room data request handler.
    Allows to receive latest game state.
    """

    async def get(self, room_id: str) -> None:
        """Get the latest game room state"""
        room = await Room.get(id=room_id).select_related("game")
        engine = get_engine(room)
        # this is public endpoint, user could be missed
        user_id = str(self.request.user.id) if self.request.user else None
        data = await engine.poll(user_id)
        # wrap up in object -> {"data": {...}}
        self.write(dict(data=data))


class RoomGameTurnHandler(BaseRequestHandler):
    """
    Game Turn data request handler.
    Allows to make a game turn.
    """

    async def _close_room(self, room_id: Id) -> None:
        """Update room status to closed"""
        room = await Room.get(id=room_id)
        room.status = GameRoomStatus.FINISHED.value
        room.closed = datetime.now()
        await room.save(
            update_fields=(
                "closed",
                "status",
            )
        )

    @login_required
    async def post(self, room_id: str) -> None:
        """Create a game turn"""
        user_id = str(self.request.user.id)
        turn = tornado.escape.json_decode(self.request.body)
        if not turn:
            raise APIError(400, "Validation error")
        room = await Room.get(id=room_id).select_related("game")
        engine = get_engine(room)
        # update game state
        data, status = await engine.update(user_id, turn)
        if not engine.is_in_progress(status):
            await self._close_room(room.id)
        self.write(dict(data=data))


class RoomPlayersHandler(BaseRequestHandler):
    """
    Room players request handler.
    Let add and remove room participants.
    """

    @login_required
    async def post(self, room_id: str) -> None:
        """join room"""
        player_id = self.request.arguments.get("user_id")
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).prefetch_related("participants")
        player_already_joined = await room.participants.filter(id=player_id).exists()
        if not room or player_already_joined:
            raise APIError(400, "User already joined the room.")
        await room.participants.add(current_user)
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.set_status(201)
        self.write(dict(data=serializer.model_dump(mode="json")))

    @login_required
    async def delete(self, room_id: str, player_id: str) -> None:
        """Player could cancel own participation"""
        # TODO: dry it!
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).select_related("admin").prefetch_related("participants")
        player_participate = any(filter(lambda p: p.id == current_user.id, room.participants))  # type: ignore
        if not (room and player_participate):
            raise APIError(400, "User aren't participant of the room.")
        await room.participants.remove(current_user)
        if not len(await room.participants.all()):
            # cancel room if there are no participants
            room.status = GameRoomStatus.CANCELED.value
            room.closed = datetime.now()
            await room.save(
                update_fields=(
                    "closed",
                    "status",
                )
            )
        self.set_status(204)
