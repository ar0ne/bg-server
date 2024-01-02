"""App services"""
from datetime import datetime

from aiocache import cached
from tortoise.contrib.pydantic.base import PydanticListModel, PydanticModel

from core.constants import GameRoomStatus
from core.loaders import get_engine
from core.resources.errors import APIError
from core.resources.models import (
    Game,
    GameListSerializer,
    GameSerializer,
    Player,
    PlayerSerializer,
    Room,
    RoomListSerializer,
    RoomSerializer,
)


class GameService:
    """Game service"""

    @cached(key="all_games", alias="default")
    async def get_all_games(self) -> list[dict]:
        """Get all games"""
        list_serializer = await GameListSerializer.from_queryset(Game.all())
        return list_serializer.model_dump(mode="json")

    @cached(key_builder=lambda _, __, n: f"get_game_{n}".lower(), alias="default")
    async def get_game_by_name(self, name) -> dict:
        """Get game details by name"""
        game = await Game.get(name=name)
        serializer = await GameSerializer.from_tortoise_orm(game)
        return serializer.model_dump(mode="json")


class PlayerService:
    """Player service"""

    @cached(key_builder=lambda _, __, i: f"get_player_id_{i}", alias="default")
    async def get_player_by_id(self, player_id: str) -> dict:
        """Get player data by id"""
        player = await Player.get(id=player_id)
        serializer = await PlayerSerializer.from_tortoise_orm(player)
        return serializer.model_dump(mode="json")


class RoomService:
    """Room service"""

    async def create_room(self, game_id: str, user, room_size: int | None) -> dict:
        game = await Game.get(id=game_id)
        size = room_size or game.min_size
        room = await Room.create(
            admin=user, game=game, status=GameRoomStatus.CREATED.value, size=size
        )
        await room.participants.add(user)
        serializer = await RoomSerializer.from_tortoise_orm(room)
        return serializer.model_dump(mode="json")

    async def get_available_rooms(
        self,
    ) -> list[dict]:
        """Get available rooms"""
        list_serializer: PydanticListModel = await RoomListSerializer.from_queryset(Room.all())
        return list_serializer.model_dump(mode="json")

    async def get_room_by_id(self, room_id: str) -> dict:
        """Get room details by id"""
        room = await Room.get(id=room_id).select_related("game")
        serializer: PydanticModel = await RoomSerializer.from_tortoise_orm(room)
        return serializer.model_dump(mode="json")

    async def join_room(self, room_id: str, user) -> dict:
        """Join a room"""
        room = await Room.get(id=room_id).prefetch_related("participants")
        if await room.participants.filter(id=user.id).exists():
            raise APIError(400, "User already joined the room.")
        await room.participants.add(user)
        serializer = await RoomSerializer.from_tortoise_orm(room)
        return serializer.model_dump(mode="json")

    async def leave_room(self, room_id: str, user) -> None:
        """Leave a room"""
        room = await Room.get(id=room_id).select_related("admin").prefetch_related("participants")
        user_participate = any(filter(lambda p: p.id == user.id, room.participants))  # type: ignore
        if not user_participate:
            raise APIError(400, "User is not in the list of participants.")
        await room.participants.remove(user)
        if not len(await room.participants.all()):
            # cancel room if there are no participants
            room.status = GameRoomStatus.CANCELED.value
            room.closed = datetime.now()
            await room.save(
                update_fields=(
                    "closed",
                    "status",
                )
            )

    async def update_room(self, room_id: str, user, data: dict) -> dict:
        """update room"""
        room = await Room.get(id=room_id).select_related("game")
        if user.id != room.admin_id:  # type: ignore
            raise APIError(401, "Can't perform this action.")

        # FIXME: add validation
        if "size" in data:
            if room.game.min_size < data["size"] > room.game.max_size:
                raise Exception  # FIXME: raise validation error
            room.size = data["size"]
        if "status" in data:
            status = data["status"]
            room.status = GameRoomStatus(status).value
            if status == GameRoomStatus.STARTED.value:
                players_ids = list(
                    map(str, await room.participants.all().values_list("id", flat=True))
                )
                # new game event triggered
                engine = await get_engine(room)
                await engine.setup(players_ids)
        await room.save(update_fields=("status", "size"))
        serializer = await RoomSerializer.from_tortoise_orm(room)
        return serializer.model_dump(mode="json")


class GameRoomService:
    """Game room service"""

    async def get_game_room_state(self, room_id: str, user_id: str | None) -> dict:
        """Get room game state data"""
        room = await Room.get(id=room_id).select_related("game")
        engine = await get_engine(room)
        # this is public endpoint, user could be missed
        return await engine.poll(user_id)

    async def _close_room(self, room_id: str) -> None:
        """Update room status to closed"""
        room = await Room.get(id=room_id)
        room.status = GameRoomStatus.FINISHED.value
        room.closed = datetime.now()
        await room.save(
            update_fields=(
                "closed",
                "status",
            )
        )

    async def make_turn(self, room_id: str, user, turn: dict) -> dict:
        """Make a game turn"""
        room = await Room.get(id=room_id).select_related("game")
        engine = await get_engine(room)
        # update game state
        data, status = await engine.update(str(user.id), turn)
        if not engine.is_in_progress(status):
            await self._close_room(room_id)
        return data


game_service = GameService()
player_service = PlayerService()
room_service = RoomService()
game_room_service = GameRoomService()
