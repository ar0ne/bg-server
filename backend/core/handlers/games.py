"""Game handler"""
import time

from core.resources.handlers import BaseRequestHandler
from core.services import game_service


class GameHandler(BaseRequestHandler):
    """
    Games request handler.
    """

    async def get(self, game_name: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_name:
            data = dict(results=await game_service.get_all_games())
        else:
            data = dict(data=await game_service.get_game_by_name(game_name))
        self.write(data)
