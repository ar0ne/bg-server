"""DTO"""
import json
from dataclasses import asdict, dataclass, is_dataclass
from typing import List, Tuple

FlatCard = Tuple[str, str]


@dataclass(frozen=True)
class GameData:
    """Represents internal game state data"""

    enemy_deck: List[FlatCard]
    discard_deck: List[FlatCard]
    first_player_id: str
    players: List[Tuple[str, List[FlatCard]]]
    played_combos: List[List[FlatCard]]
    state: str
    tavern_deck: List[FlatCard]
    turn: int
