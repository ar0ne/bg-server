"""Base game interface"""
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Union

Id = Union[str, uuid.UUID]
GameData = Dict[str, Any]
GameDataTurn = Dict[str, Any]
GameState = Any  # FIXME
Game = Type["AbstractGame"]


class AbstractGame(ABC):
    """Base game interface"""

    @abstractmethod
    async def setup(self, players: List[Id]) -> None:
        """game setup"""

    @abstractmethod
    async def update(self, player_id: Id, turn: GameDataTurn) -> None:
        """update game state"""

    @abstractmethod
    async def poll(self, player_id: Optional[Id] = None) -> GameData | None:
        """poll game state"""

    @abstractmethod
    async def is_valid_turn(self, player_id: Id, turn: GameDataTurn) -> bool:
        """True if it's valid game turn"""


class GameDataSerializer(ABC):
    """Abstract game data serializer"""

    @classmethod
    @abstractmethod
    def serialize(cls, game: AbstractGame, player_id: Id | None = None) -> Any:
        """Serialize game state to turn data dto object"""


class GameLoader(ABC):
    """Abstract game loader"""

    @staticmethod
    @abstractmethod
    def load(state: Any) -> Game:
        """Load data from state"""

    @staticmethod
    @abstractmethod
    def upload(game: Game) -> GameState:
        """Upload game state"""
