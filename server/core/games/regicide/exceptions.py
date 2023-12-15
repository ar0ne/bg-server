"""Regicide errors"""

from core.games.exceptions import GameLogicError, ValidationError

# FIXME: provide error messages


class CardDoesNotBelongsToPlayerError(GameLogicError):
    """Card doesn't belong to player"""


class MaxComboSizeExceededError(GameLogicError):
    """Exceeded max size of the combo"""


class InvalidPairComboError(GameLogicError):
    """Pair combo is invalid"""


class InvalidTurnDataError(ValidationError):
    """invalid turn data error"""


class InvalidCardDataError(ValidationError):
    """Invalid card error"""
