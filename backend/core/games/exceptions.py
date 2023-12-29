"""Game exceptions"""
from core.resources.errors import Error, ValidationError


class GameLogicError(Error):
    """Generic error in Game Logic"""

    status_code = 500


class InvalidGameStateError(GameLogicError):
    """Invalid game state error"""


class GameDataNotFound(Error):
    """Game data not found"""


class TurnOrderViolationError(ValidationError):
    """Another player's turn"""

    error_code = "GE01"
    error_message = "Wrong turn order"
