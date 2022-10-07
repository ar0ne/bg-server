"""Game handler"""

import tornado

from server.app.models import Game
from server.handlers.base import BaseRequestHandler


class GameHandler(BaseRequestHandler):
    """Games handler"""

    @tornado.web.authenticated
    async def get(self, game_name: str = "") -> None:
        """Get game or all games endpoint"""
        if not game_name:
            games = await Game.all()
            self.render("games.html", games=games)
            return
        game = await Game.get(name=game_name)
        await self.render("game.html", game=game)
