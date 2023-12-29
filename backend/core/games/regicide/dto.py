"""DTO"""
from dataclasses import dataclass
from typing import List, Tuple

from core.utils import Serializable

FlatCard = Tuple[str, str]


@dataclass(frozen=True)
class PlayerHand(Serializable):
    id: str
    size: int
    hand: List[FlatCard] | None = None


@dataclass(frozen=True)
class GameStateDto(Serializable):
    """Represents internal game state data"""

    enemy_deck: List[FlatCard]
    discard_deck: List[FlatCard]
    active_player_id: str
    players: List[Tuple[str, List[FlatCard]]]
    played_combos: List[List[FlatCard]]
    status: str
    tavern_deck: List[FlatCard]
    turn: int


@dataclass(frozen=True)
class GameTurnDataDto(Serializable):
    """Represents game turn data"""

    enemy_deck_size: int
    discard_size: int
    enemy: FlatCard | None
    enemy_state: Tuple[int | None, int | None]
    active_player_id: str
    player_id: str
    played_combos: List[List[FlatCard]]
    status: str
    tavern_size: int
    turn: int
    hands: List[PlayerHand]
