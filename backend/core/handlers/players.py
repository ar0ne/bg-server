"""Player handler"""
from core.resources.auth import login_required
from core.resources.handlers import BaseRequestHandler
from core.services import player_service


class PlayerHandler(BaseRequestHandler):
    """Player info handler"""

    @login_required
    async def get(self, player_id: str) -> None:
        """Render public info about player"""
        self.write(dict(player=await player_service.get_player_by_id(player_id)))
