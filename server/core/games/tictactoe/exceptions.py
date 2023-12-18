"""TicTacToe game exceptions"""
from core.resources.errors import ValidationError


class InvalidTurnData(ValidationError):
    """Invalid turn data"""

    error_code = "TT01"
    error_message = "Invalid turn data"


class CellAlreadyUsedError(ValidationError):
    """Cell already used"""

    error_code = "TT02"
    error_message = "Cell already used"
