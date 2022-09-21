"""
Main
"""
import asyncio
import os
from datetime import datetime

import tornado.web
from pony.orm import Database, Required, PrimaryKey, Set, sql_debug, db_session, Optional, select

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")
define("db_host", default="127.0.0.1", help="database host")
define("db_port", default=5432, help="database port")
define("db_database", default="blog", help="database name")
define("db_user", default="blog", help="database user")
define("db_password", default="blog", help="database password")

db = Database("sqlite", filename=":memory:")

class Player(db.Entity):
    admin_rooms = Set("Room", reverse="admin")
    date_joined = Required(datetime)
    email = Required(str, unique=True)
    id = PrimaryKey(int, auto=True)  # FIXME: uuid4
    joined_rooms = Set("Room", reverse="participants")
    name = Required(str)
    nickname = Required(str, unique=True)
    password = Required(str)


class Game(db.Entity):
    id = PrimaryKey(int, auto=True)  # FIXME: uuid4
    name = Required(str)
    games = Set("Room")


class Room(db.Entity):
    admin = Required(Player)
    date_closed = Optional(datetime)
    date_created = Required(datetime)
    game = Required(Game)
    id = PrimaryKey(int, auto=True)  # FIXME: uuid4
    participants = Set(Player)
    status = Required(int)  # FIXME: Enum?


def create_database():

    sql_debug(True)

    db.generate_mapping(create_tables=True)

    with db_session:
        game = Game(name="Regicide")
        joe = Player(
            date_joined=datetime.now(),
            email="joe@pl.er",
            name="Joe",
            nickname="joe",
            password="123",
        )
        bob = Player(
            date_joined=datetime.now(),
            email="bob@pl.er",
            name="Bob",
            nickname="bob",
            password="123",
        )
        room = Room(
            admin=joe, date_created=datetime.now(), game=game, participants=[joe, bob], status=1
        )




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



async def main() -> None:
    """Main loop function"""

    parse_command_line()

    create_database()
    app = Application(db)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
