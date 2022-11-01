"""Room handlers"""
from typing import Optional

import tornado

from server.resources.models import Game, Player, Room, RoomListSerializer, RoomSerializer
from server.constants import GameRoomStatus
from server.games.regicide.adapter import RegicideGameAdapter
from resources.handlers import BaseRequestHandler

class RoomHandler(BaseRequestHandler):
    """Room request handler"""

    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            # FIXME: add limit
            # FIXME: filter open to join pages only
            serializer = await RoomListSerializer.from_queryset(Room.all())
            self.write(serializer.json())
        else:
            room = await Room.filter(id=room_id).select_related("admin").first() if room_id else None
            serializer = await RoomSerializer.from_tortoise_orm(room)
            self.write(serializer.json())

    @tornado.web.authenticated
    async def post(self, room_id: str) -> None:
        """Admin could update the status of the room to start the game"""
        room = (
            await Room.get(id=room_id)
            .select_related("admin", "game")
            .prefetch_related("participants")
        )
        if self.current_user != room.admin:
            raise Exception  # FIXME
        status = GameRoomStatus(int(self.get_argument("status")))
        room.status = status.value
        await room.save()
        # TODO: server should notify all participants about this changes
        # TODO: we have to resolve which game manager to use and how?
        players_ids = await room.participants.all().values_list("id", flat=True)
        await RegicideGameAdapter(room.id).setup(players_ids)
        self.redirect(self.get_argument("next", f"/rooms/{room_id}"))

    async def put(self, room_id: str) -> None:
        """Player could make game turns"""
        room = await Room.get(id=room_id).select_related("game")
        data = tornado.escape.json_decode(self.request.body)
        turn = data["data"]
        # FIXME: ensure we know current user that sent request
        user_id = self.current_user.id if self.current_user else None
        await RegicideGameAdapter(room.id).update(user_id, turn)


class RoomPlayersHandler(BaseRequestHandler):
    """Room players handler"""

    @tornado.web.authenticated
    async def post(self, room_id: str) -> None:
        """join room"""
        player_id = self.get_argument("player_id")
        player = self.current_user
        if str(player.id) != player_id:
            raise Exception  # FIXME
        room = await Room.get(id=room_id).prefetch_related("participants")
        player_already_joined = await room.participants.filter(id__in=player_id).exists()
        if not room or player_already_joined:
            raise Exception  # FIXME
        await room.participants.add(player)
        self.redirect(f"/rooms/{room_id}")

    @tornado.web.authenticated
    async def delete(self, room_id: str) -> None:
        """Player could cancel own participation"""
        # TODO: dry it!
        player_id = self.get_argument("player_id")
        player = self.current_user
        if str(player.id) != player_id:
            raise Exception  # FIXME
        room = await Room.get(id=room_id).prefetch_related("participants")
        player_joined = await room.participants.filter(id__in=player_id).exists()
        if not (room and player_joined):
            raise Exception  # FIXME
        await room.participants.remove(player)
        self.redirect(f"/rooms/{room_id}")


class GameRoomHandler(BaseRequestHandler):
    """Game room handler"""

    async def post(self, game_name: str) -> None:
        """Create game room"""
        admin_id = self.get_argument("admin")
        admin = await Player.get(id=admin_id)
        game = await Game.get(name=game_name)
        room = await Room.create(admin=admin, game=game, status=GameRoomStatus.CREATED.value)
        await room.participants.add(admin)

        players = await room.participants.all()
        game = await room.game.get()
        data = dict(room=room, players=players, game=game)
        await self.render("room.html", **data)
