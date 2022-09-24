"""Server handlers"""
from typing import Optional

import bcrypt
import tornado

from server.app.models import Player, Game, Room, GameData
from server.app.utils import JsonDecoderMixin
from server.constants import COOKIE_USER_KEY, REGICIDE, GameRoomStatus
from server.games.regicide.game import Game as RegicideGame
from server.games.regicide.utils import dump_data


class BaseRequestHandler(JsonDecoderMixin, tornado.web.RequestHandler):
    """Base request handler"""

    async def prepare(self):
        # get_current_user cannot be a coroutine, so set
        # self.current_user in prepare instead.
        if self.current_user:
            return
        user_id = self.get_secure_cookie(COOKIE_USER_KEY)
        if not user_id:
            return
        self.current_user = await Player.filter(id=user_id.decode("utf-8")).first()


class MainHandler(BaseRequestHandler):
    """Main request handler"""

    async def get(self) -> None:
        rooms = await Room.filter(status=GameRoomStatus.CREATED.value)
        game = await Game.get(name=REGICIDE)
        game_id = game.id if game else None
        # FIXME: we have only single game atm
        data = dict(rooms=rooms, game_id=game_id)
        await self.render("index.html", **data)


class AuthSignUpHandler(BaseRequestHandler):
    async def get(self) -> None:
        """render sign up page"""
        await self.render("sign_up.html")

    async def post(self) -> None:
        email = self.get_argument("email")
        # validation ?
        if await Player.exists(email=email):
            raise tornado.web.HTTPError(400, "player with email %s already registered" % email)

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.hashpw,
            tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt(),
        )
        await Player.create(
            email=email,
            nickname=self.get_argument("nickname"),
            password=tornado.escape.to_unicode(hashed_password),
        )
        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseRequestHandler):
    def get(self):
        """render login page"""
        self.render("login.html", error=None)

    async def post(self):
        email = self.get_argument("email")
        player = await Player.filter(email=email).first()
        if not player:
            await self.render("login.html", error="email not found")
            return
        password_equal = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.checkpw,
            tornado.escape.utf8(self.get_argument("password")),
            tornado.escape.utf8(player.password),
        )
        if password_equal:
            self.set_secure_cookie(COOKIE_USER_KEY, str(player.id))
            self.redirect(self.get_argument("next", "/"))
        else:
            await self.render("login.html", error="incorrect user or password")


class AuthLogoutHandler(BaseRequestHandler):
    def get(self):
        self.clear_cookie(COOKIE_USER_KEY)
        self.redirect(self.get_argument("next", "/"))


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
            data["data"] = await GameData.filter(room=room, game=game).first()
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
        regicide = RegicideGame(players_ids)
        regicide.start_new_game()
        dump = dump_data(regicide)
        await GameData.create(game=room.game, room=room, dump=dump)
        self.redirect(self.get_argument("next", f"/rooms/{room_id}"))


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


class GameHandler(BaseRequestHandler):
    """Games handler"""

    @tornado.web.authenticated
    async def get(self, game_name: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_name:
            games = await Game.all()
            self.render("games.html", games=games)
            return
        game = await Game.get(name=game_name)
        await self.render("game.html", game=game)


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


class PlayerHandler(BaseRequestHandler):
    """Player info handler"""

    @tornado.web.authenticated
    async def get(self, player_id: str) -> None:
        """Render public info about player"""
        player = await Player.get(id=player_id)
        self.render("player.html", player=player)
