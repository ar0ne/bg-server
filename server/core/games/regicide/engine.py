"""Regicide game engine"""
from typing import Any, Tuple, cast

from core.games.engine import BaseGameEngine
from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Regicide
from core.games.regicide.models import Status
from core.games.regicide.serializers import (
    RegicideGameStateDataSerializer,
    RegicideGameTurnDataSerializer,
)
from core.games.serializers import GameStateDataSerializer, GameTurnDataSerializer
from core.types import GameDataTurn, GameState


class RegicideGameEngine(BaseGameEngine):
    """Regicide game engine"""

    STATUSES_IN_PROGRESS = (
        Status.CREATED.value,
        Status.PLAYING_CARDS.value,
        Status.DISCARDING_CARDS.value,
    )

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
        game: Regicide = self.state_serializer.loads(game_data_dto)  # type: ignore
        # update game state
        game = game.make_turn(player_id, turn)
        # save changes
        game_state = self.state_serializer.dumps(game)
        await self.save(game_state)
        # return turn game state for the player
        turn_game_state = self.turn_serializer.dumps(game, player_id=player_id)
        return turn_game_state, game.status.value

    async def poll(self, player_id: str | None = None) -> GameState:
        """Poll the last turn data"""
        game_data_dto = await self.get_game_data_dto()
        game: Regicide = self.state_serializer.loads(game_data_dto)  # type: ignore
        # we can't just return latest game state, because players don't know full game state and
        # don't see same data. We partially serialize game state (turn) with data player could see
        turn_game_state = self.turn_serializer.dumps(game, player_id=player_id)
        return turn_game_state

    async def get_game_data_dto(self) -> GameStateDto:
        """Get game data and prepare it for load"""
        return GameStateDto(**await self.get_game_data())

    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""
        return game_status in self.STATUSES_IN_PROGRESS


def create_engine(room_id: str) -> RegicideGameEngine:
    """Game engine builder"""
    return RegicideGameEngine(
        game_cls=Regicide,
        room_id=room_id,
        state_serializer=cast(GameStateDataSerializer, RegicideGameStateDataSerializer),
        turn_data_serializer=cast(GameTurnDataSerializer, RegicideGameTurnDataSerializer),
    )
