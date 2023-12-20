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
        # different players could see different turn data
        self.turn_serializer = turn_data_serializer
        # cant serialize state data to game object and back
        self.state_serializer = state_serializer

    async def setup(self, players: List[str]) -> None:
        """Setup new game"""
        game = Game.start_new_game(players)
        await self._save_game_state(game)

    async def update(self, player_id: str, turn_data: GameDataTurn) -> Tuple[GameData, str]:
        """Update game state"""
        # transform from flat cards to Card objects
        last_game_data = await self._get_latest_game_state()
        game = self.state_serializer.load(last_game_data)
        # update game state
        game = Game.make_turn(game, str(player_id), turn_data)
        # save changes
        await self._save_game_state(game)
        # return updated game state to player
        turn_data = self.turn_serializer.dump(game, player_id=player_id)
        return asdict(turn_data), game.status

    async def poll(self, player_id: str | None = None) -> GameData | None:
        """Poll the last turn data"""
        last_game_data = await self._get_latest_game_state()
        game = self.state_serializer.load(last_game_data)
        # we can't just return latest game state here, because players don't see the same
        # so, we init game instance and dump it to hide other players hands
        player_id = str(player_id) if player_id else None
        turn_data = self.turn_serializer.dump(game, player_id=player_id)
        return asdict(turn_data)

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
    def create_engine(cls, room_id: str) -> Self:
        """Factory for engine"""
        return cls(
            room_id=room_id,
            turn_data_serializer=RegicideGameTurnDataSerializer(),
            state_serializer=RegicideGameStateDataSerializer(),
        )
