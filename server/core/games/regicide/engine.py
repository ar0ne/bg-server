"""Regicide game engine"""
from typing import Any, List, Self, Tuple, cast

from core.games.engine import BaseGameEngine
from core.games.exceptions import GameDataNotFound
from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Regicide
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

    async def update(self, player_id: str, turn: GameDataTurn) -> Tuple[GameState, str]:
        """Update game state"""
        # transform from flat cards to Card objects
        game_data_dto = await self.get_game_data_dto()
        game: Regicide = self.state_serializer.load(game_data_dto)  # type: ignore
        # update game state
        game = game.make_turn(player_id, turn)
        # save changes
        game_state = self.state_serializer.dump(game)
        await self.save(game_state)
        # return turn game state for the player
        turn_game_state = self.turn_serializer.dump(game, player_id=player_id)
        return turn_game_state, game.status.value

    async def poll(self, player_id: str | None = None) -> GameState:
        """Poll the last turn data"""
        game_data_dto = await self.get_game_data_dto()
        game: Regicide = self.state_serializer.load(game_data_dto)  # type: ignore
        # we can't just return latest game state here, because players don't see the same data
        # so, we need serialize game state with only data player could know
        turn_game_state = self.turn_serializer.dump(game, player_id=player_id)
        return turn_game_state

    async def get_game_data_dto(self) -> GameStateDto:
        """Get game data and prepare it for load"""
        return GameStateDto(**await self.get_game_data())


def create_engine(room_id: str) -> RegicideGameEngine:
    """Game engine builder"""
    return RegicideGameEngine(
        game_cls=Regicide,
        room_id=room_id,
        state_serializer=cast(GameStateDataSerializer, RegicideGameStateDataSerializer),
        turn_data_serializer=cast(GameTurnDataSerializer, RegicideGameTurnDataSerializer),
    )
