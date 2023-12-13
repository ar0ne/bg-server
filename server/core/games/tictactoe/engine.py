"""Tic Tac Toe game engine"""
from dataclasses import asdict
from typing import List

from core.games.base import AbstractGame, GameData, GameDataTurn, Id
from core.games.tictactoe.converters import TicTacToeGameStateDataConverter
from core.games.tictactoe.dto import GameStateDto
from core.games.tictactoe.game import Game
from core.games.tictactoe.models import Status
from core.resources.models import GameTurn, Player

# FIXME: move duplicated code to BaseGame class


class GameEngine(AbstractGame):
    """Game engine"""

    def __init__(self, room_id: Id) -> None:
        """init engine"""
        self.room_id = room_id
        # FIXME: add some factory to avoid dependencies
        self.state_converter = TicTacToeGameStateDataConverter

    async def setup(self, player_ids: List[Id]) -> None:
        """Setup game"""
        game = Game.start_new_game(player_ids)
        await self._save_game_state(game)

    async def update(self, player_id: Id, turn: GameDataTurn) -> None:
        """Update game state"""
        if not self.is_valid_turn(player_id, turn):
            # FIXME: do something
            pass

        # FIXME: here we need to validate if turn is valid, before save it

        last_game_data = await self._get_latest_game_state()
        game = self.state_converter.load(last_game_data)
        # FIXME: move it all to validation method
        player = game.active_player
        if not player:
            raise Exception  # FIXME
        if player.id != player_id:
            raise Exception  # FIXME
        if game.status == Status.IN_PROGRESS:
            game.make_turn(player, turn)
        else:
            raise Exception  # FIXME

        # save changes
        await self._save_game_state(game)

    async def poll(self, player: Player | None = None) -> GameData | None:
        """Poll the last game state"""
        last_turn_state = await self._get_latest_game_state()
        if not last_turn_state:
            return None
        player_id = str(player.id) if player else None
        return dict(player_id=player_id, **asdict(last_turn_state))

    async def _get_latest_game_state(self) -> GameStateDto | None:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            return None
        return GameStateDto(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        game_state = self.state_converter.dump(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=game_state)

    def is_valid_turn(self, player_id: Id, turn: GameDataTurn) -> bool:
        """True if this is valid game turn"""
        # FIXME: should we game and check current state
        return True
