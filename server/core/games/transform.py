"""Transform"""

from abc import ABC, abstractmethod
from typing import Any

from core.games.game import Game
from core.types import GameState

# FIXME: protocol instead?


class GameTurnDataSerializer(ABC):
    """Abstract game data serializer"""

    # FIXME: load ?

    @staticmethod
    @abstractmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Transform game object into state"""


class GameStateDataSerializer(ABC):
    """Abstract game state data serializer"""

    @staticmethod
    @abstractmethod
    def load(data: GameState, **kwargs) -> Game:
        """Load data from state"""

    @staticmethod
    @abstractmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Dump game state into object"""
