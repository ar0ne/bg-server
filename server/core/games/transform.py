"""Transform"""

from typing import Any, Protocol

from core.games.game import Game
from core.types import GameState


class GameTurnDataSerializer(Protocol):
    """Abstract game data serializer"""

    @staticmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Transform game object into state"""
        ...


class GameStateDataSerializer(Protocol):
    """Abstract game state data serializer"""

    @staticmethod
    def load(data: GameState, **kwargs) -> Game:
        """Load data from state"""
        ...

    @staticmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Dump game state into object"""
        ...
