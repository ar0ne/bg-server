"""Base game interface"""
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

Id = Union[str, uuid.UUID]
GameData = Dict[str, Any]
GameDataTurn = Dict[str, Any]


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
    def serialize(cls, game: AbstractGame, player_id: str | None = None) -> Any:
        """Serialize game state to turn data dto object"""
