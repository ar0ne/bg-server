"""Room handlers"""
from typing import Optional

import tornado

from server.app.models import Room, Player, Game
from server.constants import GameRoomStatus
from server.games.regicide.adapter import RegicideGameAdapter
from server.games.regicide.utils import load_data
from server.handlers.base import BaseRequestHandler
from server.games.regicide.game import Game as RegicideGame


class RoomHandler(BaseRequestHandler):
    """Room request handler"""

    @tornado.web.authenticated
    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            self.redirect(self.get_argument("next", "/"))
            return
        room = await Room.filter(id=room_id).select_related("admin").first() if room_id else None
        players = await room.participants.all()
        game = await room.game.get()
        data = dict(room=room, players=players, game=game)
        if room.status == GameRoomStatus.CREATED.value:
            room.status = GameRoomStatus(room.status).name  # hack to display beautified status
            await self.render("room.html", **data)
        else:
            user = self.current_user
            data["data"] = await RegicideGameAdapter(room.id).poll(user.id)  # TODO: game observers
            await self.render("playground.html", **data)

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

    @tornado.web.authenticated
    async def put(self, room_id: str) -> None:
        """Player could make game turns"""
        room = await Room.get(id=room_id).select_related("game")
        turn = self.get_argument("data")
        user = self.current_user
        game_data = await RegicideGameAdapter(room.id).update(user.id, turn)
        regicide = RegicideGame([self.current_user.id])
        load_data(regicide, game_data.dump)


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
