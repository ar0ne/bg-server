from server.app.models import Room, Game
from server.constants import GameRoomStatus, REGICIDE
from server.handlers.base import BaseRequestHandler


class MainHandler(BaseRequestHandler):
    """Main request handler"""

    async def get(self) -> None:
        rooms = await Room.filter(status=GameRoomStatus.CREATED.value)
        game = await Game.get(name=REGICIDE)
        game_id = game.id if game else None
        # FIXME: we have only single game atm
        data = dict(rooms=rooms, game_id=game_id)
        await self.render("index.html", **data)

