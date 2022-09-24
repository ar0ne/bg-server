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
        user_id = self.get_secure_cookie(COOKIE_USER_KEY).decode("utf-8")
        if not user_id:
            return

        self.current_user = await Player.filter(id=user_id).first()


class MainHandler(BaseRequestHandler):
    """Main request handler"""

    async def get(self) -> None:
        rooms = await Room.filter(status=0)
        game = await Game.filter(name=REGICIDE).first()
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
        player = await Player(email=email).first()
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

    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            self.redirect(self.get_argument("next", "/"))
            return
        if room_id:
            room = await Room.filter(id=room_id).first()
        await self.render("room.html", room=room)

    async def post(self, _) -> None:
        """Create game room"""
        admin_id = self.get_argument("admin")
        game_id = self.get_argument("game")
        admin = await Player.filter(id=admin_id).first()
        game = await Game.filter(id=game_id).first()
        room = await Room.create(admin=admin, game=game, status=0)
        await room.participants.add(admin)

        await self.render("room.html", room=room)
