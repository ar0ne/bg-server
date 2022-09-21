"""DB models"""

from datetime import datetime

from pony.orm import Required, Optional, PrimaryKey, Set, Database, sql_debug, db_session

db = Database()


class Player(db.Entity):
    admin_rooms = Set("Room", reverse="admin")
    date_joined = Required(datetime)
    email = Required(str, unique=True)
    id = PrimaryKey(int, auto=True)  # FIXME: uuid4
    joined_rooms = Set("Room", reverse="participants")
    name = Optional(str)
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


sql_debug(True)

def init_fake_data():
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
