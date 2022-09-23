"""DTO"""
from dataclasses import dataclass
from typing import List, Tuple

from server.app.games.regicide.types import FlatCard


@dataclass(frozen=True)
class GameData:
    """Represents internal game state data"""

    enemy_deck: List[FlatCard]
    discard_deck: List[FlatCard]
    first_player_id: str
    players: List[Tuple[str, List[FlatCard]]]
    state: str
    tavern_deck: List[FlatCard]
    turn: int
