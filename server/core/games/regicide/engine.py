"""Regicide game engine"""
from dataclasses import asdict
from typing import List

from core.games.base import AbstractGame, GameData, GameDataTurn, Id
from core.games.exceptions import GameDataNotFound
from core.games.regicide.converters import (
    RegicideGameStateDataConverter,
    RegicideGameTurnDataConverter,
)
from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Game, validate_game_turn
from core.games.regicide.models import Card
from core.resources.models import GameTurn, Player


class GameEngine(AbstractGame):
    """Regicide game engine"""

    def __init__(self, room_id: Id) -> None:
        """Init adapter"""
        self.room_id = room_id
        # FIXME: add some factory to avoid dependencies
        self.game_data_converter = RegicideGameTurnDataConverter
        self.game_state_converter = RegicideGameStateDataConverter

    async def setup(self, players: List[Id]) -> None:
        """Setup new game"""
        game = Game.start_new_game(players)
        await self._save_game_state(game)

    async def update(self, player_id: Id, turn: GameDataTurn) -> None:
        """Update game state"""
        # transform from flat cards to Card objects
        last_game_data = await self._get_latest_game_state()
        game = self.game_state_converter.load(last_game_data)
        validate_game_turn(game, player_id, turn)
        game.make_turn(player_id, turn)
        # save changes
        await self._save_game_state(game)

    async def poll(self, player_id: Id | None = None) -> GameData | None:
        """Poll the last turn data"""
        last_turn_state = await self._get_latest_game_state()
        game = self.game_state_converter.load(last_turn_state)
        # we can't just return latest game state here, because players don't see the same
        # so, we init game instance and dump it to hide other players hands
        player_id = str(player_id) if player_id else None
        game_turn = self.game_data_converter.dump(game, player_id=player_id)
        return asdict(game_turn)

    async def _get_latest_game_state(self) -> GameStateDto | None:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            raise GameDataNotFound
        return GameStateDto(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        game_state = self.game_state_converter.dump(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=game_state)
