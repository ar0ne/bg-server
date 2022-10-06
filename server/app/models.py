"""DB models"""
import json

from tortoise import Model, fields

from server.app.utils import CustomJSONEncoder
from server.constants import REGICIDE, GameRoomStatus

JSON_ENCODER = lambda x: json.dumps(x, cls=CustomJSONEncoder)


class Player(Model):
    """Player model"""

    date_joined = fields.DatetimeField(auto_now_add=True)
    email = fields.TextField(email=True)
    id = fields.UUIDField(pk=True)
    name = fields.TextField(null=True)
    nickname = fields.CharField(unique=True, max_length=60)
    password = fields.TextField()


class Game(Model):
    """Game model"""

    id = fields.UUIDField(pk=True)
    name = fields.CharField(unique=True, max_length=50)




class Room(Model):
    """Room model"""

    admin = fields.ForeignKeyField("models.Player", related_name="admin_rooms")
    date_closed = fields.DatetimeField(null=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    game = fields.ForeignKeyField("models.Game", related_name="rooms")
    id = fields.UUIDField(pk=True)
    participants = fields.ManyToManyField("models.Player", related_name="")
    status = fields.SmallIntField()


class GameTurn(Model):
    """Temporary model to store game state"""

    id = fields.UUIDField(pk=True)
    turn = fields.SmallIntField(default=0)
    room = fields.ForeignKeyField("models.Room")
    # FIXME: get rid of it
    data = fields.JSONField(encoder=JSON_ENCODER)


async def init_fake_data():
    game = await Game.create(name=REGICIDE)
    foo = await Player.create(
        email="foo@f.oo",
        name="Foo",
        nickname="foo",
        password="$2b$12$5LAFLk9LJlem6ZUH2KmZO.T81anazVEcqoMZjZ5ezzmS7b13JUQeS",
    )
    await Player.create(
        email="bar@b.ar",
        name="Bar",
        nickname="bar",
        password="$2b$12$5LAFLk9LJlem6ZUH2KmZO.T81anazVEcqoMZjZ5ezzmS7b13JUQeS",
    )
    room = await Room.create(admin=foo, game=game, status=GameRoomStatus.CREATED.value)
    await room.participants.add(foo)
