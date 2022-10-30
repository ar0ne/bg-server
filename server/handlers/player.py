"""Player handler"""
import tornado

from server.resources.models import Player
from server.handlers.base import BaseRequestHandler


class PlayerHandler(BaseRequestHandler):
    """Player info handler"""

    @tornado.web.authenticated
    async def get(self, player_id: str) -> None:
        """Render public info about player"""
        player = await Player.get(id=player_id)
        self.render("player.html", player=player)
