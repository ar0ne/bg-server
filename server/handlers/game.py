"""Game handler"""

from server.resources.models import Game, GameListSerializer, GameSerializer
from resources.handlers import BaseRequestHandler


class GameHandler(BaseRequestHandler):
    """Games handler"""

    async def get(self, game_name: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_name:
            serializer = await GameListSerializer.from_queryset(Game.all())
        else:
            game = await Game.get(name=game_name)
            serializer = await GameSerializer.from_tortoise_orm(game)
        self.write(serializer.json())
