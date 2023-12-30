"""Game handler"""
import time

from core.resources.handlers import BaseRequestHandler
from core.services import GameService


class GameHandler(BaseRequestHandler):
    """
    Games request handler.
    """

    game_service = GameService()

    async def get(self, game_name: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_name:
            data = dict(results=await self.game_service.get_all_games())
        else:
            data = dict(data=await self.game_service.get_game_by_name(game_name))
        self.write(data)
