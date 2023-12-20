"""Base game interface"""
import uuid
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Dict, List, Type, Union

Id = Union[str, uuid.UUID]
GameData = Dict[str, Any]
GameDataTurn = Dict[str, Any]
GameState = Any  # FIXME
Game = Any  # FIXME


class AbstractGame(ABC):
    """Base game interface"""

    @abstractmethod
    async def setup(self, player_ids: List[str]) -> None:
        """game setup"""

    @abstractmethod
    async def update(self, player_id: str, turn: GameDataTurn) -> GameData | None:
        """update game state"""

    @abstractmethod
    async def poll(self, player_id: str | None = None) -> GameData | None:
        """poll game state"""

    @abstractmethod
    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""

    @abstractclassmethod
    def create_engine(cls, room_id: str) -> "AbstractGame":
        """factory for game engines"""
