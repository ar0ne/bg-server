"""
Main
"""
from datetime import datetime
from typing import Optional

import bcrypt
import asyncio
import os

import tornado.web
from pony.orm import db_session, select, Database, commit

from tornado.options import define, options, parse_command_line, parse_config_file

from server.app import models
from server.app.models import Room, init_fake_data, Player
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
        user_id = self.get_secure_cookie(COOKIE_USER_KEY)
        if not user_id:
            return
        with db_session:
            self.current_user = select(
                p for p in Player if str(p.id) == user_id.decode("utf-8")
            ).first()


class MainHandler(BaseRequestHandler):
    """Main request handler"""

    async def get(self) -> None:
        with db_session:
            rooms = select(r for r in Room if r.status != 0)
        data = dict(title="Hello world", rooms=rooms)
        await self.render("index.html", **data)


class RoomHandler(BaseRequestHandler):
    """Room request handler"""

    async def get(self, room_id: Optional[str] = None) -> None:
        if not room_id:
            self.redirect(self.get_argument("next", "/"))
            return
        if room_id:
            with db_session:
                room = select(r for r in Room if r.id == room_id).first()
        await self.render("room.html", room=room)

    # @db_session
    # def post(self):
    #


class AuthSignUpHandler(BaseRequestHandler):
    async def get(self) -> None:
        """render sign up page"""
        await self.render("sign_up.html")

    async def post(self) -> None:
        email = self.get_argument("email")
        # validation ?
        with db_session:
            if Player.exists(email=email):
                raise tornado.web.HTTPError(400, "player with email %s already registered" % email)

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.hashpw,
            tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt(),
        )
        with db_session:
            Player(
                email=email,
                nickname=self.get_argument("nickname"),
                password=tornado.escape.to_unicode(hashed_password),
                date_joined=datetime.now(),
            )
            commit()

        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseRequestHandler):
    def get(self):
        """render login page"""
        self.render("login.html", error=None)

    async def post(self):
        email = self.get_argument("email")
        with db_session:
            player = select(p for p in Player if p.email == email).first()
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
            (r"/auth/sign-up", AuthSignUpHandler),
            (r"/auth/login", AuthLoginHandler),
            (r"/auth/logout", AuthLogoutHandler),
            (r"/rooms/(.*)", RoomHandler),
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


def init_database() -> Database:
    """Initialize database"""
    db = models.db
    db_settings = dict(
        provider=options.db_provider,
        user=options.db_user,
        password=options.db_password,
        host=options.db_host,
        port=options.db_port,
        database=options.db_database,
    )
    if options.db_provider == "sqlite":
        db_settings = dict(provider=options.db_provider, filename=":memory:")

    db.bind(**db_settings)
    db.generate_mapping(create_tables=True)
    return db


async def main() -> None:
    """Main loop function"""
    parse_command_line()
    parse_config_file(CONFIG_FILE_PATH)

    db = init_database()
    init_fake_data()  # FIXME: remove it later

    app = Application(db)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
