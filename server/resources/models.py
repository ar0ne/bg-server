"""DB models"""
import json

from tortoise import Model, fields, Tortoise
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from server.resources.utils import CustomJSONEncoder
from server.constants import REGICIDE, GameRoomStatus

JSON_ENCODER = lambda x: json.dumps(x, cls=CustomJSONEncoder)


class Player(Model):
    """Player model"""

    date_joined = fields.DatetimeField(auto_now_add=True)
    email = fields.CharField(email=True, unique=True, max_length=50)
    id = fields.UUIDField(pk=True)
    name = fields.CharField(unique=True, max_length=60)
    nickname = fields.CharField(unique=True, null=True, max_length=60)
    password = fields.CharField(max_length=120)

    class PydanticMeta:
        exclude = (
            "password",
        )


class Game(Model):
    """Game model"""

    id = fields.UUIDField(pk=True)
    name = fields.CharField(unique=True, max_length=50)

    # description
    # image

    class PydanticMeta:
        exclude = (
            "rooms",
        )


class Room(Model):
    """Room model"""

    admin: fields.ForeignKeyRelation[Player] = fields.ForeignKeyField("models.Player", related_name="admin_rooms")
    date_closed = fields.DatetimeField(null=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    game: fields.ForeignKeyRelation["Game"] = fields.ForeignKeyField("models.Game", related_name="rooms")
    id = fields.UUIDField(pk=True)
    participants: fields.ManyToManyRelation[Player] = fields.ManyToManyField("models.Player", related_name="")
    status = fields.SmallIntField()

    def room_state(self) -> str:
        """get room state"""
        CREATED = "created"
        PLAYING_CARDS = "playing_cards"
        DISCARDING_CARDS = "discarding_cards"
        LOST = "lost"
        WON = "won"
        MAP = {1: CREATED, 2: PLAYING_CARDS, 3: DISCARDING_CARDS, 4: LOST, 5: WON}
        return MAP[self.status]

    class PydanticMeta:
        exclude = ["gameturns", "status"]
        computed = ["room_state"]


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


Tortoise.init_models(["server.resources.models"], "models")

PlayerSerializer = pydantic_model_creator(Player)
PlayerListSerializer = pydantic_queryset_creator(Player)
RoomSerializer = pydantic_model_creator(Room)
RoomListSerializer = pydantic_queryset_creator(Room)
GameSerializer = pydantic_model_creator(Game)
GameListSerializer = pydantic_queryset_creator(Game)
