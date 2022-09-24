"""Server handlers"""
from typing import Optional

import bcrypt
import tornado

from server.app.models import Player, Game, Room
from server.app.utils import JsonDecoderMixin
from server.constants import COOKIE_USER_KEY, REGICIDE


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
        rooms = await Room.filter(status=0)
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
        room = await Room.filter(id=room_id).first() if room_id else None
        players = await room.participants.all()
        game = await room.game.get()
        data = dict(room=room, players=players, game=game)
        await self.render("room.html", **data)


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


class GameHandler(BaseRequestHandler):
    """Games handler"""

    @tornado.web.authenticated
    async def get(self, game_id: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_id:
            games = await Game.all()
            self.render("games.html", games=games)
            return
        game = await Game.get(id=game_id)
        await self.render("game.html", game=game)


class GameRoomHandler(BaseRequestHandler):
    """Game room handler"""

    async def post(self, game_id: str) -> None:
        """Create game room"""
        admin_id = self.get_argument("admin")
        admin = await Player.get(id=admin_id)
        game = await Game.get(id=game_id)
        room = await Room.create(admin=admin, game=game, status=0)
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