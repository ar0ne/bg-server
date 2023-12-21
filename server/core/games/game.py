from abc import ABC, abstractclassmethod, abstractmethod
from typing import List, Self, Type, TypeVar

from core.types import GameDataTurn

T = TypeVar("T", bound="Game")


# mypy: disable-error-code=empty-body
class Game(ABC):
    """Game interface"""

    @abstractclassmethod
    def init_new_game(cls: Type[T], player_ids: List[str]) -> Type[T]:
        """Init new game session"""

    @abstractmethod
    def make_turn(self: T, player_id: str, turn: GameDataTurn) -> T:
        """Make a turn"""
