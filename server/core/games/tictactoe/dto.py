"""TicTacToe DTO"""

from dataclasses import dataclass
from typing import List, Tuple

from core.utils import Serializable


@dataclass(frozen=True)
class GameStateDto(Serializable):
    """Represents internal game state data"""

    active_player_id: str | None
    players: List[str]
    board: List[str | None]
    status: str
    turn: int
    winner_id: str | None = None
