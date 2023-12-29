"""Transform"""

from typing import Protocol

from core.games.game import Game
from core.types import GameState


class GameTurnDataSerializer(Protocol):
    """Abstract game data serializer"""

    @staticmethod
    def dumps(game: Game, /, player_id: str | None) -> GameState:
        """Transform game object into state"""
        ...


class GameStateDataSerializer(Protocol):
    """Abstract game state data serializer"""

    @staticmethod
    def loads(data: GameState, /) -> Game:
        """Load data from state"""
        ...

    @staticmethod
    def dumps(game: Game, /) -> GameState:
        """Dump game state into object"""
        ...
