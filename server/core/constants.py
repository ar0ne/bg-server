"""App constants"""
import enum


class GameRoomStatus(enum.Enum):
    """Represents current state of the game room"""

    CREATED = 0
    STARTED = 1
    CANCELED = 2
    FINISHED = 3
    ABANDONED = 4
