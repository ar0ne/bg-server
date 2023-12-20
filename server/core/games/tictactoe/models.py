"""TicTacToe models"""

import enum
from typing import List

from core.types import Id


class Player:
    """Player"""

    def __init__(self, id: Id) -> None:
        """Init player object"""
        self.id = str(id)

    def __str__(self) -> str:
        """to string"""
        return self.id

    def __eq__(self, other) -> bool:
        """True if object are equal"""
        if isinstance(other, Player):
            return self.id == other.id
        return False


class Status(enum.Enum):
    """Enum for game status"""

    CREATED = "created"
    DRAW = "draw"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABANDONED = "abandoned"
