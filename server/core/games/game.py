from abc import ABC, abstractclassmethod
from typing import List

from core.types import GameDataTurn


class Game(ABC):
    """Game interface"""

    @abstractclassmethod
    def init_new_game(cls, player_ids: List[str]) -> "Game":
        """Init new game session"""

    @abstractclassmethod
    def make_turn(game: "Game", player_id: str, turn: GameDataTurn) -> "Game":
        """Make a turn"""
