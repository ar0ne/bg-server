"""Regicide errors"""

from core.games.exceptions import GameLogicError

# FIXME: provide error messages


class CardBelongsToAnotherError(GameLogicError):
    """Card doesn't belong to player"""


class MaxComboSizeExceededError(GameLogicError):
    """Exceeded max size of the combo"""


class InvalidPairComboError(GameLogicError):
    """Pair combo is invalid"""
