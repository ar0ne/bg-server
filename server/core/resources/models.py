"""DB models"""
import json

from core.constants import REGICIDE, TICTACTOE, GameRoomStatus
from core.resources.utils import CustomJSONEncoder
from core.types import Id
from tortoise import Model, Tortoise, fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

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
        exclude = ("password",)


class Game(Model):
    """Game model"""

    id = fields.UUIDField(pk=True)
    name = fields.CharField(unique=True, max_length=50)
    min_size = fields.SmallIntField(default=1)
    max_size = fields.SmallIntField(default=1)

    # description
    # image

    class PydanticMeta:
        exclude = ("rooms",)


class Room(Model):
    """Room model"""

    admin: fields.ForeignKeyRelation[Player] = fields.ForeignKeyField(
        "models.Player", related_name="admin_rooms"
    )
    closed = fields.DatetimeField(null=True)
    created = fields.DatetimeField(auto_now_add=True)
    game: fields.ForeignKeyRelation["Game"] = fields.ForeignKeyField(
        "models.Game", related_name="rooms"
    )
    id: Id = fields.UUIDField(pk=True)
    participants: fields.ManyToManyRelation[Player] = fields.ManyToManyField(
        "models.Player", related_name=""
    )
    size: int = fields.SmallIntField(default=1)
    status: int = fields.SmallIntField(default=0)

    class PydanticMeta:
        exclude = ("gameturns",)


class GameTurn(Model):
    """Temporary model to store game state"""

    # FIXME: get rid of it
    data = fields.JSONField(encoder=JSON_ENCODER)
    id: Id = fields.UUIDField(pk=True)
    room: Room = fields.ForeignKeyField("models.Room")
    turn: int = fields.SmallIntField(default=0)


Tortoise.init_models(["core.resources.models"], "models")

PlayerSerializer = pydantic_model_creator(Player)
PlayerListSerializer = pydantic_queryset_creator(Player)
RoomSerializer = pydantic_model_creator(Room)
RoomListSerializer = pydantic_queryset_creator(Room)
GameSerializer = pydantic_model_creator(Game)
GameListSerializer = pydantic_queryset_creator(Game)


async def initial_data():
    """Initial data"""
    await Game.get_or_create(name=REGICIDE, min_size=1, max_size=4)
    await Game.get_or_create(name=TICTACTOE, min_size=2, max_size=2)
