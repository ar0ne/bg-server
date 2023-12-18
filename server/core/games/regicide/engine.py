"""Regicide game engine"""
from dataclasses import asdict
from typing import List, Self, Tuple

from core.games.base import AbstractGame, GameData, GameDataTurn
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

STATUSES_IN_PROGRESS = (Status.CREATED, Status.PLAYING_CARDS, Status.DISCARDING_CARDS)


class GameEngine(AbstractGame):
    """Regicide game engine"""

    def __init__(
        self,
        room_id: str,
        turn_data_serializer: GameTurnDataSerializer,
        state_serializer: GameStateDataSerializer,
    ) -> None:
        """Init game engine"""
        self.room_id = room_id
        self.game_data_serializer = turn_data_serializer
        self.game_state_serializer = state_serializer

    async def setup(self, players: List[str]) -> None:
        """Setup new game"""
        game = Game.start_new_game(players)
        await self._save_game_state(game)

    async def update(self, player_id: str, turn: GameDataTurn) -> Tuple[GameData, str]:
        """Update game state"""
        # transform from flat cards to Card objects
        last_game_data = await self._get_latest_game_state()
        game = self.game_state_serializer.load(last_game_data)
        game = Game.make_turn(game, str(player_id), turn)
        # save changes
        await self._save_game_state(game)
        # return updated game state for player
        game_turn = self.game_data_serializer.dump(game, player_id=player_id)
        return asdict(game_turn), game.status

    async def poll(self, player_id: str | None = None) -> GameData | None:
        """Poll the last turn data"""
        last_turn_state = await self._get_latest_game_state()
        game = self.game_state_serializer.load(last_turn_state)
        # we can't just return latest game state here, because players don't see the same
        # so, we init game instance and dump it to hide other players hands
        player_id = str(player_id) if player_id else None
        game_turn = self.game_data_serializer.dump(game, player_id=player_id)
        return asdict(game_turn)

    async def _get_latest_game_state(self) -> GameStateDto | None:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            raise GameDataNotFound
        return GameStateDto(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        game_state = self.game_state_serializer.dump(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=game_state)

    def is_in_progress(self, game_status: str) -> bool:
        """True if game is in progress"""
        return game_status in STATUSES_IN_PROGRESS

    @classmethod
    def create_engine(cls, room_id: str) -> Self:
        """Factory for engine"""
        return cls(
            room_id=room_id,
            turn_data_serializer=RegicideGameTurnDataSerializer(),
            state_serializer=RegicideGameStateDataSerializer(),
        )
