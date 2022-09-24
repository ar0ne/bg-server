"""
Main
"""
from datetime import datetime
from typing import Optional

import bcrypt
import asyncio
import os

import tornado.web

from tornado.options import define, options, parse_command_line, parse_config_file
from tortoise import Tortoise

from server.app.constants import REGICIDE
from server.app.models import Room, Player, Game, init_fake_data
from server.app.utils import JsonDecoderMixin

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
define("db_provider", default="sqlite", help="database provider")
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="", help="database name")
define("db_user", default="", help="database user")
define("db_password", default="", help="database password")

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
COOKIE_USER_KEY = "user-cookie-key"


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
        room = await Room.create(
            admin=admin, date_created=datetime.now(), game=game, status=0
        )
        await room.participants.add(admin)

        await self.render("room.html", room=room)


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
            date_joined=datetime.now(),
        )
        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseRequestHandler):
    def get(self):
        """render login page"""
        self.render("login.html", error=None)

    async def post(self):
        email = self.get_argument("email")
        player = await Player(email = email).first()
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
            await self.render("login.html", error="incorrect password")


class AuthLogoutHandler(BaseRequestHandler):
    def get(self):
        self.clear_cookie(COOKIE_USER_KEY)
        self.redirect(self.get_argument("next", "/"))


class Application(tornado.web.Application):
    """Application"""

    def __init__(self, db):
        """Init application"""
        self.db = db
        handlers = [
            (r"/auth/sign-up/?", AuthSignUpHandler),
            (r"/auth/login/?", AuthLoginHandler),
            (r"/auth/logout/?", AuthLogoutHandler),
            (r"/rooms/?(.*)", RoomHandler),
            (r"/", MainHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=options.debug,
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=True,
        )
        super().__init__(handlers, **settings)


async def init_database() -> None:
    """Initialize database"""

    db_settings = dict(
        provider=options.db_provider,
        user=options.db_user,
        password=options.db_password,
        host=options.db_host,
        port=options.db_port,
        database=options.db_database,
    )
    if options.db_provider == "sqlite":
        # FIXME: fix for other db providers
        await Tortoise.init(
            db_url="sqlite://:memory:",
            modules={'models': ['server.app.models']}
        )
    # Generate the schema
    await Tortoise.generate_schemas()

async def main() -> None:
    """Main loop function"""
    parse_command_line()
    parse_config_file(CONFIG_FILE_PATH)

    await init_database()
    await init_fake_data()  # FIXME: remove it later

    app = Application(None)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
