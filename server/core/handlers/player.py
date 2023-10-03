"""Player handler"""
from core.resources.auth import login_required
from core.resources.handlers import BaseRequestHandler
from core.resources.models import Player, PlayerSerializer


class PlayerHandler(BaseRequestHandler):
    """Player info handler"""

    @login_required
    async def get(self, player_id: str) -> None:
        """Render public info about player"""
        player = await Player.get(id=player_id)
        serializer = await PlayerSerializer.from_tortoise_orm(player)
        self.write(serializer.json())
