"""Room handlers"""
from datetime import datetime
from typing import Optional

import tornado
from core.constants import GameRoomStatus
from core.resources.auth import login_required
from core.resources.errors import APIError
from core.resources.handlers import BaseRequestHandler
from core.resources.models import Game, Player, Room, RoomListSerializer, RoomSerializer


async def get_room_player_id(room: Room, user: Optional[Player]) -> Optional[str]:
    """Get user id if user participate in game room"""
    if not user:
        return None
    players_ids = await room.participants.all().values_list("id", flat=True)
    if user.id in players_ids:
        return str(user.id)
    return None


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
        self.write(serializer.model_dump_json())


class RoomHandler(BaseRequestHandler):
    """
    Room request handler.
    Allows to get all available game rooms, room details, setup room (and start game).
    """

    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            # FIXME: add limit
            # FIXME: filter open to join pages only
            serializer = await RoomListSerializer.from_queryset(Room.all())
            self.write(serializer.model_dump_json())
        else:
            room = await Room.get(id=room_id).select_related("game")
            serializer = await RoomSerializer.from_tortoise_orm(room)
            self.write(serializer.model_dump_json())

    @login_required
    async def put(self, room_id: str) -> None:
        """Player could make game turns"""
        current_user = self.request.user
        room = await Room.get(id=room_id).select_related("game")
        if current_user.id != room.admin_id:
            raise APIError(401, "Can't perform this action.")

        # FIXME: add validation
        data = self.request.arguments
        if "status" in data:
            status = data["status"]
            room.status = GameRoomStatus(status).value
            if status == GameRoomStatus.STARTED.value:
                players_ids = await room.participants.all().values_list("id", flat=True)
                # new game event triggered
                engine = room.game.get_engine()(room_id)
                await engine.setup(players_ids)

        if "size" in data:
            room.size = data["size"]
        await room.save(update_fields=("status", "size"))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.model_dump_json())


class RoomDataHandler(BaseRequestHandler):
    """
    Game Room data request handler.
    Allows to receive latest game state.
    """

    async def get(self, room_id: str) -> None:
        """Get the latest game room state"""
        room = await Room.get(id=room_id).select_related("game")
        player_id = await get_room_player_id(room, self.request.user)
        engine = room.game.get_engine()(room_id)
        data = await engine.poll(player_id)
        # wrap up in object -> {"data": {...}}
        self.write(dict(data=data))


class RoomGameTurnHandler(BaseRequestHandler):
    """
    Game Turn data request handler.
    Allows to make a game turn.
    """

    async def post(self, room_id: str) -> None:
        """Create a game turn"""
        turn = tornado.escape.json_decode(self.request.body)
        if not turn:
            raise APIError(400, "Validation error")
        room = await Room.get(id=room_id).select_related("game")
        player_id = await get_room_player_id(room, self.request.user)
        if not player_id:
            raise APIError(403, "Unauthorized action.")  # FIXME: auth decorator?
        engine = room.game.get_engine()(room_id)
        if not engine.is_valid_turn(player_id, turn):
            raise APIError(400, "Invalid turn.")
        await engine.update(player_id, turn)
        # FIXME: notify all players (observers) => WS ?
        data = await engine.poll(self.request.user)
        self.write(data)


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
        player_already_joined = await room.participants.filter(id__in=player_id).exists()
        if not room or player_already_joined:
            raise APIError(400, "User already joined the room.")
        await room.participants.add(current_user)
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.model_dump_json())

    @login_required
    async def delete(self, room_id: str, player_id: str) -> None:
        """Player could cancel own participation"""
        # TODO: dry it!
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).select_related("admin").prefetch_related("participants")
        is_admin = current_user.id == room.admin.id
        player_participate = any(filter(lambda p: p.id == current_user.id, room.participants))
        if not (room and player_participate):
            raise APIError(400, "User aren't participant of the room.")
        await room.participants.remove(current_user)
        if is_admin and not len(await room.participants.all()):
            # cancel room if there are no participants
            room.status = GameRoomStatus.CANCELED.value
            room.closed = datetime.now()
            await room.save(update_fields=("status",))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.model_dump_json())
