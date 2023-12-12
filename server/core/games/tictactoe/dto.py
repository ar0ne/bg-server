"""TicTacToe DTO"""

from dataclasses import dataclass
from typing import List, Tuple


@dataclass(frozen=True)
class GameStateDto:
    """Represents internal game state data"""

    active_player_id: str
    # [[None, <player-1-id>, <player-2-id>], [None, ...]]
    players: List[str]
    board: List[List[str | None]]
    state: str
    turn: int


@dataclass(frozen=True)
class GameTurnDataDto:
    """Represents game turn data"""

    active_player_id: str
    # cell_idx: int | None
    player_id: str
    state: str
    turn: int
