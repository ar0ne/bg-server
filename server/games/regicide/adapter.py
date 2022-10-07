"""Regicide game adapter"""
from typing import Dict, Any, List

from server.app.models import GameTurn
from server.games.base import AbstractGame, Id
from server.games.regicide.game import Game
from server.games.regicide.utils import dump_data


class RegicideGameAdapter(AbstractGame):
    """Regicide game adapter"""

    def __init__(self, room_id: Id) -> None:
        """Init adapter"""
        self.room_id = room_id

    async def setup(self, players: List[Id]) -> None:
        """Setup new game"""
        regicide = Game.start_new_game(players)
        dump = dump_data(regicide)
        await GameTurn.create(room_id=self.room_id, data=dump)

    async def update(self, player: Id, data: Dict[str, Any]) -> None:
        """Update game state"""
        pass

    async def poll(self, player: Id) -> Dict[str, Any]:
        """Poll the last turn data"""
        last_turn_data = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        # data should be for specific player only
        return last_turn_data or {}


    