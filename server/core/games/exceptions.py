"""Game exceptions"""


# TODO: provide error messages


class Error(Exception):
    """Base error class"""


class GameLogicError(Error):
    """Generic error in Game Logic"""


class InvalidGameStateError(GameLogicError):
    """Invalid game state error"""


class TurnOrderViolationError(GameLogicError):
    """Another player's turn"""


class GameDataNotFound(Error):
    """Game data not found"""


class ValidationError(Error):
    """Validation error"""
