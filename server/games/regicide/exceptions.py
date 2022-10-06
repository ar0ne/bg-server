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


class CardBelongsToAnotherError(GameLogicError):
    """Card doesn't belong to player"""


class MaxComboSizeExceededError(GameLogicError):
    """Exceeded max size of the combo"""


class InvalidPairComboError(GameLogicError):
    """Pair combo is invalid"""
