"""Player handler"""
from core.resources.auth import login_required
from core.resources.handlers import BaseRequestHandler
from core.resources.models import Player, PlayerSerializer
from core.services import PlayerService


class PlayerHandler(BaseRequestHandler):
    """Player info handler"""

    player_service = PlayerService()

    @login_required
    async def get(self, player_id: str) -> None:
        """Render public info about player"""
        self.write(dict(player=await self.player_service.get_player_by_id(player_id)))
