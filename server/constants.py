"""App constants"""
import enum

REGICIDE = "Regicide"
COOKIE_USER_KEY = "user-cookie-key"


class GameRoomStatus(enum.Enum):
    """Represents current state of the game room"""

    # FIXME: add status PLAYING ? to prevent duplicated new game trigger
    CREATED = 0
    STARTED = 1
    CANCELED = 2
    FINISHED = 3
    ABANDONED = 4
