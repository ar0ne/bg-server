"""TicTacToe models"""

import enum
from typing import List


class Player:
    """Player"""

    def __init__(self, id: str) -> None:
        """Init player object"""
        self.id = id

    def __str__(self) -> str:
        """to string"""
        return self.id


class Board:
    """
    Game board
    """

    def __init__(self, items: List[str] | None = None, size: int = 3) -> None:
        """Init board"""
        self.size = size
        self.items = items if items else [None] * self.size**2

    def __getitem__(self, idx):
        return self.items[idx]

    def __setitem__(self, idx, val):
        self.items[idx] = val


class Status(enum.Enum):
    """Enum for game status"""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABANDONED = "abandoned"
