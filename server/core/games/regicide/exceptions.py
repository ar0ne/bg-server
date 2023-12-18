"""Regicide errors"""
from core.games.exceptions import GameLogicError
from core.resources.errors import ValidationError


class CardDoesNotBelongsToPlayerError(ValidationError):
    """Card doesn't belong to player"""

    error_code = "RG01"
    error_message = "Card does not belong to player"


class MaxComboSizeExceededError(ValidationError):
    """Exceeded max size of the combo"""

    error_code = "RG02"
    error_message = "Max combo size exceeded"


class InvalidPairComboError(ValidationError):
    """Pair combo is invalid"""

    error_code = "RG03"
    error_message = "Invalid pair combo"


class InvalidTurnDataError(ValidationError):
    """invalid turn data error"""

    error_code = "RG04"
    error_message = "Invalid turn data"


class InvalidCardDataError(ValidationError):
    """Invalid card error"""

    error_code = "RG05"
    error_message = "Invalid card"


class NotEnoughPowerToDiscard(ValidationError):
    """Not enough cards power to defeat attack"""

    error_code = "RG06"
    error_message = "Not enough cards power to defeat attack"
