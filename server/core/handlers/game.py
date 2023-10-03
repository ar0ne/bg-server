"""Game handler"""

from core.resources.handlers import BaseRequestHandler
from core.resources.models import Game, GameListSerializer, GameSerializer


class GameHandler(BaseRequestHandler):
    """
    Games request handler.
    Let get games list, and game details.
    """

    async def get(self, game_name: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_name:
            serializer = await GameListSerializer.from_queryset(Game.all())
        else:
            game = await Game.get(name=game_name)
            serializer = await GameSerializer.from_tortoise_orm(game)
        self.write(serializer.json())
