"""Regicide game adapter"""
from typing import Dict, Any, List

from server.app.models import GameTurn
from server.games.base import BaseGame, Id
from server.games.regicide.game import Game
from server.games.regicide.utils import dump_data


class RegicideGameAdapter(BaseGame):
    """Regicide game adapter"""

    async def setup(self, players: List[Id]) -> None:
        """Setup new game"""
        regicide = Game(players)
        regicide.start_new_game()
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


    