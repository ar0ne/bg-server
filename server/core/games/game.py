from abc import ABC, abstractmethod
from typing import List, Self, Type, TypeVar

from core.types import GameDataTurn

G = TypeVar("G", bound="Game")


# mypy: disable-error-code=empty-body
class Game(ABC):
    """Game interface"""

    @classmethod
    @abstractmethod
    def init_new_game(cls: Type[G], player_ids: List[str]) -> G:
        """Init new game session"""

    @abstractmethod
    def make_turn(self: Self, player_id: str, turn: GameDataTurn) -> Self:
        """Make a turn"""
