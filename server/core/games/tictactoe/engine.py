"""Tic Tac Toe game engine"""
from typing import Tuple, cast

from core.games.engine import BaseGameEngine
from core.games.tictactoe.dto import GameStateDto
from core.games.tictactoe.game import TicTacToe
from core.games.tictactoe.models import Status
from core.games.tictactoe.serializers import TicTacToeGameStateDataSerializer
from core.games.transform import GameStateDataSerializer
from core.types import GameDataTurn, GameState


class TicTacToeGameEngine(BaseGameEngine):
    """TicTacToe game engine"""

    STATUSES_IN_PROGRESS = (Status.CREATED, Status.IN_PROGRESS)

    async def update(self, player_id: str, turn: GameDataTurn) -> Tuple[GameState, str]:
        """Update game state"""
        game_data_dto = await self.get_game_data_dto()
        game: TicTacToe = self.state_serializer.load(game_data_dto)  # type: ignore
        # update state
        game = game.make_turn(player_id, turn)
        # save changes
        game_state = self.state_serializer.dump(game)
        await self.save(game_state)
        # serialize updated game state
        return game_state, game.status.value

    async def poll(self, player_id: str | None = None) -> GameState:
        """Poll the last game state"""
        game_data_gto = await self.get_game_data_dto()
        player_id = str(player_id) if player_id else None
        # we don't need to hide anything from other users, just serialize state
        return dict(player_id=player_id, **game_data_gto.asdict())

    async def get_game_data_dto(self) -> GameStateDto:
        """Get game data and prepare it for load"""
        return GameStateDto(**await self.get_game_data())


def create_engine(room_id: str) -> TicTacToeGameEngine:
    """Game engine builder"""
    return TicTacToeGameEngine(
        game_cls=TicTacToe,
        room_id=room_id,
        state_serializer=cast(GameStateDataSerializer, TicTacToeGameStateDataSerializer),
    )
