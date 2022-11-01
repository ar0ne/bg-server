"""DB models"""
import enum
import json
from typing import Optional

from tortoise import Model, Tortoise, fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from server.constants import REGICIDE, GameRoomStatus
from server.resources.utils import CustomJSONEncoder

JSON_ENCODER = lambda x: json.dumps(x, cls=CustomJSONEncoder)


class RoomState(enum.Enum):
    CREATED = (0, "created")
    STARTED = (1, "playing_cards")
    FINISHED = (2, "finished")
    ABANDONED = (3, "abandoned")
    CANCELLED = (4, "cancelled")

    def __init__(self, state: int, label: str) -> None:
        """Init room state enum"""
        self.state = state
        self.label = label

    @classmethod
    def from_value(cls, value: int) -> Optional["RoomState"]:
        """
        Return enum object if value exists.

        >>> RoomState.ABANDONED is not RoomState.from_value(4)
        >>> RoomState.ABANDONED is RoomState.from_value(3)
        """
        for _, v in RoomState.__members__.items():
            if v.value[0] == value:
                return v
        return None


class Player(Model):
    """Player model"""

    date_joined = fields.DatetimeField(auto_now_add=True)
    email = fields.CharField(email=True, unique=True, max_length=50)
    id = fields.UUIDField(pk=True)
    name = fields.CharField(unique=True, max_length=60)
    nickname = fields.CharField(unique=True, null=True, max_length=60)
    password = fields.CharField(max_length=120)

    class PydanticMeta:
        exclude = ("password",)


class Game(Model):
    """Game model"""

    id = fields.UUIDField(pk=True)
    name = fields.CharField(unique=True, max_length=50)

    # description
    # image

    class PydanticMeta:
        exclude = ("rooms",)


class Room(Model):
    """Room model"""

    admin: fields.ForeignKeyRelation[Player] = fields.ForeignKeyField(
        "models.Player", related_name="admin_rooms"
    )
    date_closed = fields.DatetimeField(null=True)
    date_created = fields.DatetimeField(auto_now_add=True)
    game: fields.ForeignKeyRelation["Game"] = fields.ForeignKeyField(
        "models.Game", related_name="rooms"
    )
    id = fields.UUIDField(pk=True)
    participants: fields.ManyToManyRelation[Player] = fields.ManyToManyField(
        "models.Player", related_name=""
    )
    status = fields.SmallIntField()

    def room_state(self) -> str:
        """get room state"""
        room_state_enum = RoomState.from_value(self.status)
        if not room_state_enum:
            return ""
        return room_state_enum.value[1]

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
