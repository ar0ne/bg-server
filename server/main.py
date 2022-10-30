"""
Main
"""
import asyncio
import os

import tornado.web
from tornado.options import define, options, parse_command_line, parse_config_file
from tortoise import Tortoise

from server.handlers.auth import AuthLoginHandler, AuthLogoutHandler, AuthSignUpHandler
from server.handlers.game import GameHandler
from server.handlers.index import MainHandler
from server.handlers.player import PlayerHandler
from server.handlers.room import GameRoomHandler, RoomHandler, RoomPlayersHandler

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
define("db_provider", default="sqlite", help="database provider")
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="", help="database name")
define("db_user", default="", help="database user")
define("db_password", default="", help="database password")

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


class Application(tornado.web.Application):
    """Application"""

    def __init__(self, db):
        """Init application"""
        self.db = db
        handlers = [
            (r"/auth/sign-up/?", AuthSignUpHandler),
            (r"/auth/login/?", AuthLoginHandler),
            (r"/auth/logout/?", AuthLogoutHandler),
            (r"/games/(\w+)/rooms/?", GameRoomHandler),
            (r"/games/(\w+)/?", GameHandler),
            (r"/games/?", GameHandler),
            (r"/rooms/([a-zA-Z0-9_.-]+)/players/?", RoomPlayersHandler),
            (r"/rooms/([a-zA-Z0-9_.-]+)/?", RoomHandler),
            (r"/rooms/?", RoomHandler),
            (r"/players/([a-zA-Z0-9_.-]+)/?", PlayerHandler),
            (r"/", MainHandler),
        ]
        settings = dict(
            cookie_secret="__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
            debug=options.debug,
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            xsrf_cookies=True,
            login_url="/auth/login/"
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
        # await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["server.app.models"]})
        await Tortoise.init(db_url="sqlite://db.sqlite", modules={"models": ["server.app.models"]})
    # Generate the schema
    await Tortoise.generate_schemas()


async def main() -> None:
    """Main loop function"""
    parse_command_line()
    parse_config_file(CONFIG_FILE_PATH)

    await init_database()

    # from server.app.models import init_fake_data
    # await init_fake_data()  # FIXME: remove it later

    app = Application(None)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
