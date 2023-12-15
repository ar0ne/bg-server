"""DTO"""
from dataclasses import dataclass
from typing import List, Optional, Tuple

FlatCard = Tuple[str, str]


@dataclass
class PlayerHand:
    id: str
    size: int
    hand: List[FlatCard] | None = None


@dataclass(frozen=True)
class GameStateDto:
    """Represents internal game state data"""

    enemy_deck: List[FlatCard]
    discard_deck: List[FlatCard]
    first_player_id: str
    players: List[Tuple[str, List[FlatCard]]]
    played_combos: List[List[FlatCard]]
    status: str
    tavern_deck: List[FlatCard]
    turn: int


@dataclass(frozen=True)
class GameTurnDataDto:
    """Represents game turn data"""

    enemy_deck_size: int
    discard_size: int
    enemy: FlatCard
    enemy_state: Tuple[int, int]
    first_player_id: str
    player_id: str
    played_combos: List[List[FlatCard]]
    status: str
    tavern_size: int
    turn: int
    hands: List[PlayerHand]
