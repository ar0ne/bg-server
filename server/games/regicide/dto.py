"""DTO"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

FlatCard = Tuple[str, str]


@dataclass(frozen=True)
class GameState:
    """Represents internal game state data"""

    enemy_deck: List[FlatCard]
    discard_deck: List[FlatCard]
    first_player_id: str
    players: List[Tuple[str, List[FlatCard]]]
    played_combos: List[List[FlatCard]]
    state: str
    tavern_deck: List[FlatCard]
    turn: int


@dataclass(frozen=True)
class GameTurnData:
    """Represents game turn data"""

    enemy_deck_size: int
    discard_size: int
    enemy: FlatCard
    first_player_id: str
    player_id: str
    played_combos: List[List[FlatCard]]
    state: str
    tavern_size: int
    turn: int
    hand: Optional[List[FlatCard]] = None
