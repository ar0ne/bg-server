"""
Main
"""
import asyncio
import os

import tornado.web
from pony.orm import db_session, select, Database

from tornado.options import define, options, parse_command_line, parse_config_file

from server.app import models
from server.app.models import Room

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
define("db_provider", default="sqlite", help="database provider")
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="", help="database name")
define("db_user", default="", help="database user")
define("db_password", default="", help="database password")

CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")


class BaseRequestHandler(tornado.web.RequestHandler):
    """Base request handler"""


class MainHandler(BaseRequestHandler):
    """Main request handler"""

    @db_session
    def get(self) -> None:
        rooms = select(r for r in Room if r.status != 0)
        for r in rooms:
            self.write("Room %s (%s)" % (r.id, r.status))


class Application(tornado.web.Application):
    """Application"""

    def __init__(self, db):
        """Init application"""
        self.db = db
        handlers = [
            (r"/", MainHandler),
        ]
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            debug=options.debug,
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
    app = Application(db)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
