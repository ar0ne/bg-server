"""Base game interface"""
import uuid

from abc import ABC, abstractmethod
from typing import List, Union, Dict, Any

Id = Union[str, uuid.UUID]


class AbstractGame(ABC):
    """Base game interface"""

    @abstractmethod
    async def setup(self, players: List[Id]) -> None:
        """game setup"""

    @abstractmethod
    async def update(self, player: Id, data: Dict[str, Any]) -> None:
        """update game state"""

    @abstractmethod
    async def poll(self, player: Id) -> Dict[str, Any]:
        """poll game state"""