"""App constants"""
import enum

REGICIDE = "Regicide"
COOKIE_USER_KEY = "user-cookie-key"


class GameRoomStatus(enum.Enum):
    """Represents current state of the game room"""

    CREATED = 0
    PLAYING = 1
    CANCELED = 2
    FINISHED = 3
