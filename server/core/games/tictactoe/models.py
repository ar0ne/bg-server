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


class Status(enum.Enum):
    """Enum for game status"""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABANDONED = "abandoned"
