"""Regicide game engine"""
from typing import Any, List, Self, Tuple

from core.games.base import BaseGameEngine, GameEngine
from core.games.exceptions import GameDataNotFound
from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Game
from core.games.regicide.models import Card, Status
from core.games.regicide.serializers import (
    RegicideGameStateDataSerializer,
    RegicideGameTurnDataSerializer,
)
from core.games.transform import GameStateDataSerializer, GameTurnDataSerializer
from core.resources.models import GameTurn, Player
from core.types import GameData, GameDataTurn, GameState


class RegicideGameEngine(BaseGameEngine):
    """Regicide game engine"""

    STATUSES_IN_PROGRESS = (Status.CREATED, Status.PLAYING_CARDS, Status.DISCARDING_CARDS)

    def __init__(
        self,
        game_cls: Any,
        room_id: str,
        state_serializer: GameStateDataSerializer,
        turn_data_serializer: GameTurnDataSerializer,
    ) -> None:
        """Init game engine"""
        super().__init__(game_cls, room_id, state_serializer)
        self.turn_serializer = turn_data_serializer

    async def update(self, player_id: str, turn_data: GameDataTurn) -> Tuple[GameData, str]:
        """Update game state"""
        # transform from flat cards to Card objects
        game_data_dto = await self.get_game_data_dto()
        game = self.state_serializer.load(game_data_dto)
        # update game state
        game = self.game_cls.make_turn(game, str(player_id), turn_data)
        # save changes
        game_state = self.state_serializer.dump(game)
        await self.save(game_state)
        # return updated game state to player
        turn_data = self.turn_serializer.dump(game, player_id=player_id)
        return turn_data, game.status

    async def poll(self, player_id: str | None = None) -> GameData:
        """Poll the last turn data"""
        game_data_dto = await self.get_game_data_dto()
        game = self.state_serializer.load(game_data_dto)
        # we can't just return latest game state here, because players don't see the same
        # so, we init game instance and dump it to hide other players hands
        player_id = str(player_id) if player_id else None
        turn_data = self.turn_serializer.dump(game, player_id=player_id)
        return turn_data

    async def get_game_data_dto(self) -> GameStateDto:
        """Get game data and prepare it for load"""
        return GameStateDto(**await self.get_game_data())


def create_engine(room_id: str) -> GameEngine:
    """Game engine builder"""
    return RegicideGameEngine(
        game_cls=Game,
        room_id=room_id,
        state_serializer=RegicideGameStateDataSerializer,
        turn_data_serializer=RegicideGameTurnDataSerializer,
    )
