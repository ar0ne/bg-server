"""Transform"""

from abc import ABC, abstractmethod
from typing import Any

from .base import Game, GameState

# FIXME: protocol instead?


class GameTurnDataConverter(ABC):
    """Abstract game data converter"""

    # FIXME: load ?

    @staticmethod
    @abstractmethod
    def dump(game: Game, **kwargs) -> Any:
        """Transfor game state to turn data dto object"""


class GameStateDataConverter(ABC):
    """Abstract game state data converter"""

    @staticmethod
    @abstractmethod
    def load(data: GameState, **kwargs) -> Game:
        """Load data from state"""

    @staticmethod
    @abstractmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Dump game state into object"""
