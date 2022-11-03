"""Room handlers"""
from typing import Optional

from resources.errors import APIError

from server.constants import GameRoomStatus
from server.games.regicide.adapter import RegicideGameAdapter
from server.resources.auth import login_required
from server.resources.handlers import BaseRequestHandler
from server.resources.models import Game, Player, Room, RoomListSerializer, RoomSerializer


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
            room = (
                await Room.filter(id=room_id).select_related("admin").first() if room_id else None
            )
            serializer = await RoomSerializer.from_tortoise_orm(room)
            self.write(serializer.json())

    # @tornado.web.authenticated
    # async def post(self, room_id: str) -> None:
    #     """Admin could update the status of the room to start the game"""
    #     room = (
    #         await Room.get(id=room_id)
    #         .select_related("admin", "game")
    #         .prefetch_related("participants")
    #     )
    #     if self.current_user != room.admin:
    #         raise Exception  # FIXME
    #     status = GameRoomStatus(int(self.get_argument("status")))
    #     room.status = status.value
    #     await room.save()
    #     # TODO: server should notify all participants about this changes
    #     # TODO: we have to resolve which game manager to use and how?
    #     players_ids = await room.participants.all().values_list("id", flat=True)
    #     await RegicideGameAdapter(room.id).setup(players_ids)
    #     self.redirect(self.get_argument("next", f"/rooms/{room_id}"))
    #
    # async def put(self, room_id: str) -> None:
    #     """Player could make game turns"""
    #     room = await Room.get(id=room_id).select_related("game")
    #     data = tornado.escape.json_decode(self.request.body)
    #     turn = data["data"]
    #     # FIXME: ensure we know current user that sent request
    #     user_id = self.current_user.id if self.current_user else None
    #     await RegicideGameAdapter(room.id).update(user_id, turn)


class RoomPlayersHandler(BaseRequestHandler):
    """Room players handler"""

    @login_required
    async def post(self, room_id: str) -> None:
        """join room"""
        player_id = self.get_argument("player_id")
        player = self.current_user
        if str(player.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).prefetch_related("participants")
        player_already_joined = await room.participants.filter(id__in=player_id).exists()
        if not room or player_already_joined:
            raise APIError(400, "User already joined the room.")
        await room.participants.add(player)
        serializer = RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.json())

    @login_required
    async def delete(self, room_id: str, player_id: str) -> None:
        """Player could cancel own participation"""
        # TODO: dry it!
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        room = await Room.get(id=room_id).select_related("admin").prefetch_related("participants")
        player_participate = any(filter(lambda p: p.id == current_user.id, room.participants))
        if not (room and player_participate):
            raise APIError(400, "User aren't participant of the room.")
        await room.participants.remove(current_user)
        if not (room.admin is current_user and len(room.participants)):
            # cancel room if there are no participants
            room.status = GameRoomStatus.CANCELED.value
            await room.save(update_fields=("status",))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        self.write(serializer.json())
