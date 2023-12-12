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


@dataclass(frozen=True)
class GameTurnDataDto:
    """Represents game turn data"""

    active_player_id: str
    # cell_idx: int | None
    player_id: str
    status: str
    turn: int
