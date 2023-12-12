"""TicTacToe models"""

import enum


class Player:
    """Player"""

    def __init__(self, id: str) -> None:
        """Init player object"""
        self.id = id

    def __str__(self) -> str:
        """to string"""
        return self.id


class Board:
    """Game board"""

    def __init__(self, size: int) -> None:
        """Init board"""
        self.size = size
        self.items = [[None] * self.size] * self.size


class GameState(enum.Enum):
    """Enum for game states"""

    CREATED = "created"
    IN_PROGRESS = "in_progress"
    FINISHED = "finished"
    ABANDONED = "abandoned"
