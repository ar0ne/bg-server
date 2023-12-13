"""TicTacToe DTO"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class GameStateDto:
    """Represents internal game state data"""

    active_player_id: str
    players: List[str]
    board: List[str | None]
    status: str
    turn: int
    winner_id: str | None = None
