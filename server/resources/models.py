"""DB models"""
import json

from tortoise import Model, Tortoise, fields
from tortoise.contrib.pydantic import pydantic_model_creator, pydantic_queryset_creator

from server.constants import REGICIDE, GameRoomStatus
from server.games.base import AbstractGame
from server.resources.utils import CustomJSONEncoder, lazy_import

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

    # FIXME: cache it
    def get_engine(self) -> AbstractGame:
        """Get game engine class"""
        # FIXME: used game.name instead model field and hardcoded path
        game_name = self.name.lower()
        module = lazy_import("adapter", f"server/games/{game_name}/adapter.py")
        return getattr(module, "GameEngine")

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
    size = fields.SmallIntField(default=1)
    status = fields.SmallIntField(default=0)

    def room_state(self) -> str:
        """get room state"""
        return GameRoomStatus(self.status).name

    class PydanticMeta:
        exclude = (
            "gameturns",
            "status",
        )
        computed = ("room_state",)


class GameTurn(Model):
    """Temporary model to store game state"""

    id = fields.UUIDField(pk=True)
    turn = fields.SmallIntField(default=0)
    room = fields.ForeignKeyField("models.Room")
    # FIXME: get rid of it
    data = fields.JSONField(encoder=JSON_ENCODER)


async def init_fake_data():
    game = await Game.create(name=REGICIDE, min_size=1, max_size=4)
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
    room = await Room.create(admin=foo, game=game, status=GameRoomStatus.CREATED.value, size=2)
    await room.participants.add(foo)


Tortoise.init_models(["server.resources.models"], "models")

PlayerSerializer = pydantic_model_creator(Player)
PlayerListSerializer = pydantic_queryset_creator(Player)
RoomSerializer = pydantic_model_creator(Room)
RoomListSerializer = pydantic_queryset_creator(Room)
GameSerializer = pydantic_model_creator(Game)
GameListSerializer = pydantic_queryset_creator(Game)
