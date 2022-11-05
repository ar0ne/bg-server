"""Base game interface"""
import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

Id = Union[str, uuid.UUID]


class AbstractGame(ABC):
    """Base game interface"""

    @abstractmethod
    async def setup(self, players: List[Id]) -> None:
        """game setup"""

    @abstractmethod
    async def update(self, player_id: Id, data: Dict[str, Any]) -> None:
        """update game state"""

    @abstractmethod
    async def poll(self, player_id: Optional[Id] = None) -> Dict[str, Any]:
        """poll game state"""
