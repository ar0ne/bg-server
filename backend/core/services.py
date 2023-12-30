"""App services"""
from aiocache import cached

from core.resources.models import Game, GameListSerializer, GameSerializer


class GameService:
    """Game service"""

    @cached(key="all_games", alias="default", noself=True)
    async def get_all_games(self):
        list_serializer = await GameListSerializer.from_queryset(Game.all())
        return list_serializer.model_dump(mode="json")

    @cached(key_builder=lambda _, __, n: f"get_game_{n}".lower(), alias="default", noself=True)
    async def get_game_by_name(self, name):
        game = await Game.get(name=name)
        serializer = await GameSerializer.from_tortoise_orm(game)
        return serializer.model_dump(mode="json")
