"""Tic Tac Toe game engine"""
from dataclasses import asdict
from typing import List, Self, Tuple

from core.constants import GameRoomStatus
from core.games.base import AbstractGame, GameData, GameDataTurn, Id
from core.games.exceptions import GameDataNotFound
from core.games.tictactoe.dto import GameStateDto
from core.games.tictactoe.game import Game, validate_game_turn
from core.games.tictactoe.models import Status
from core.games.tictactoe.serializers import TicTacToeGameStateDataSerializer
from core.games.transform import GameStateDataSerializer
from core.resources.models import GameTurn

STATUSES_IN_PROGRESS = (Status.CREATED, Status.IN_PROGRESS)


class GameEngine(AbstractGame):
    """TicTacToe game engine"""

    def __init__(self, room_id: Id, state_serializer: GameStateDataSerializer) -> None:
        """init game engine"""
        self.room_id = room_id
        self.state_serializer = state_serializer

    async def setup(self, player_ids: List[Id]) -> None:
        """Setup game"""
        game = Game.start_new_game(player_ids)
        await self._save_game_state(game)

    async def update(self, player_id: Id, turn: GameDataTurn) -> Tuple[GameData, Game]:
        """Update game state"""
        game_data = await self._get_latest_game_state()
        game = self.state_serializer.load(game_data)
        # always run validation before apply a turn
        validate_game_turn(game, player_id, turn)
        game = Game.make_turn(game, player_id, turn)
        # save changes
        await self._save_game_state(game)
        # serialize updated game state
        game_turn = self.state_serializer.dump(game)
        return asdict(game_turn), game

    async def poll(self, player_id: Id | None = None) -> GameData | None:
        """Poll the last game state"""
        last_state = await self._get_latest_game_state()
        player_id = str(player_id) if player_id else None
        # we don't need to hide anything from other users, just serialize state
        return dict(player_id=player_id, **asdict(last_state))

    async def _get_latest_game_state(self) -> GameStateDto:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            raise GameDataNotFound
        return GameStateDto(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        game_state = self.state_serializer.dump(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=game_state)

    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""
        return game_status in STATUSES_IN_PROGRESS

    @classmethod
    def create_engine(cls, room_id: Id) -> Self:
        return cls(
            room_id=room_id,
            state_serializer=TicTacToeGameStateDataSerializer,
        )
