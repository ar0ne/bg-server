"""Base game interface"""
import uuid
from abc import ABC, abstractclassmethod, abstractmethod
from typing import Any, Dict, List, Tuple, Type

from core.games.transform import GameStateDataSerializer
from core.resources.models import GameTurn
from core.types import GameData, GameDataTurn, GameState


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
    async def save(self, state: GameState) -> None:
        """save game state"""

    @abstractmethod
    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""

    @abstractmethod
    async def get_game_data(self) -> GameData:
        """Get the latest game state data"""


class BaseGameEngine(GameEngine):
    """Base game engine"""

    STATUSES_IN_PROGRESS = ()

    def __init__(
        self, game_cls: Any, room_id: str, state_serializer: GameStateDataSerializer
    ) -> None:
        """init game engine"""
        self.game_cls = game_cls
        self.room_id = room_id
        # cant serialize state data to game object and back
        self.state_serializer = state_serializer

    async def setup(self, players: List[str]) -> None:
        """Setup new game"""
        game = self.game_cls.init_new_game(players)
        game_state = self.state_serializer.dump(game)
        await self.save(game)

    async def save(self, state: GameState) -> None:
        """persist game state into db"""
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=state)

    async def get_game_data(self) -> GameData:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            raise GameDataNotFound
        return turn.data

    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""
        return game_status in self.STATUSES_IN_PROGRESS
