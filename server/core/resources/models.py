"""DB models"""
import json
import os

from core.constants import REGICIDE, TICTACTOE, GameRoomStatus
from core.games.base import AbstractGame, Id
from core.resources.utils import CustomJSONEncoder, lazy_import
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

    # FIXME: cache it
    def get_engine(self) -> AbstractGame:
        """Get game engine class"""
        game_name = self.name.lower()
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        module = lazy_import("engine", f"{base_dir}/core/games/{game_name}/engine.py")
        return getattr(module, "GameEngine")

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


async def init_fake_data():
    """Init fake data"""
    # game = await Game.create(name=REGICIDE, min_size=1, max_size=4)
    # game = await Game.create(name=TICTACTOE, min_size=2, max_size=2)
    # foo = await Player.create(
    #     email="foo@f.oo",
    #     name="Foo",
    #     nickname="foo",
    #     password="$2b$12$T6pXtYX5yvmw2bS4LQq5legpRNVAAox51uN8pCN50OKaF91s83s92",  # 123
    # )
    # await Player.create(
    #     email="bar@b.ar",
    #     name="Bar",
    #     nickname="bar",
    #     password="$2b$12$T6pXtYX5yvmw2bS4LQq5legpRNVAAox51uN8pCN50OKaF91s83s92",  # 123
    # )
    # room = await Room.create(admin=foo, game=game, status=GameRoomStatus.CREATED.value, size=2)
    # await room.participants.add(foo)


Tortoise.init_models(["core.resources.models"], "models")

PlayerSerializer = pydantic_model_creator(Player)
PlayerListSerializer = pydantic_queryset_creator(Player)
RoomSerializer = pydantic_model_creator(Room)
RoomListSerializer = pydantic_queryset_creator(Room)
GameSerializer = pydantic_model_creator(Game)
GameListSerializer = pydantic_queryset_creator(Game)
