"""Base game interface"""
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Type, Union

Id = Union[str, uuid.UUID]
GameData = Dict[str, Any]
GameDataTurn = Dict[str, Any]
GameState = Any  # FIXME
Game = Any  # FIXME


class AbstractGame(ABC):
    """Base game interface"""

    @abstractmethod
    async def setup(self, player_ids: List[Id]) -> None:
        """game setup"""

    @abstractmethod
    async def update(self, player_id: Id, turn: GameDataTurn) -> GameData | None:
        """update game state"""

    @abstractmethod
    async def poll(self, player_id: Id | None = None) -> GameData | None:
        """poll game state"""
