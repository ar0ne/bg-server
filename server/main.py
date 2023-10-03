"""
Main
"""
import asyncio
import os

import tornado.web
from core.handlers.routes import get_routes
from core.resources.database import init_database
from core.resources.errors import ErrorHandler
from tornado.options import define, options, parse_command_line, parse_config_file

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
define("db_provider", default="sqlite", help="database provider")
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="", help="database name")
define("db_user", default="", help="database user")
define("db_password", default="", help="database password")
define("JWT_SECRET", default="some-jwt-secret", help="JWT secret token")
define("JWT_ALGORITHM", default="HS256", help="JWT algorythm")
define("JWT_EXP_DELTA_SECONDS", default=3000, help="JWT expiration time in seconds")

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


class Application(tornado.web.Application):
    """Application"""

    def __init__(self, db):
        """Init application"""
        self.db = db
        settings = dict(
            debug=options.debug,
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            default_handler_class=ErrorHandler,
            default_handler_args=dict(status_code=404),
        )
        routes = get_routes()
        super().__init__(routes, **settings)


async def main() -> None:
    """Main loop function"""
    parse_command_line()
    parse_config_file(CONFIG_FILE_PATH)

    await init_database()

    app = Application(None)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
