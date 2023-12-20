"""Base game interface"""
import uuid
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Dict, List, Tuple, Type

from core.resources.models import GameTurn

GameData = Dict[str, Any]
GameDataTurn = Dict[str, Any]
GameState = Any  # FIXME
Game = Any  # FIXME


class GameEngine(ABC):
    """Base game interface"""

    @abstractclassmethod
    def create_engine(cls, room_id: str) -> "GameEngine":
        """factory for game engines"""

    @abstractmethod
    async def setup(self, player_ids: List[str]) -> None:
        """game setup"""

    @abstractmethod
    async def update(self, player_id: str, turn: GameDataTurn) -> Tuple[GameData, str]:
        """update game state"""

    @abstractmethod
    async def poll(self, player_id: str | None = None) -> GameData:
        """poll game state"""

    @abstractmethod
    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""

    @abstractmethod
    async def save_game_state(self, game: Game) -> None:
        """Save game state"""

    @abstractmethod
    async def get_latest_game_data(self) -> GameData:
        """Get the latest game state data"""


class BaseGameEngine(GameEngine):
    """Base game engine"""

    STATUSES_IN_PROGRESS = ()
    GAME_CLS = None

    async def setup(self, players: List[str]) -> None:
        """Setup new game"""
        game = self.GAME_CLS.start_new_game(players)
        await self.save_game_state(game)

    async def save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        game_state = self.state_serializer.dump(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=game_state)

    async def get_latest_game_data(self) -> GameData:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            raise GameDataNotFound
        return turn.data

    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""
        return game_status in self.STATUSES_IN_PROGRESS
