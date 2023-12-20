"""TicTacToe converters"""

import json

from core.games.game import Game
from core.games.tictactoe.dto import GameStateDto
from core.games.tictactoe.game import TicTacToe
from core.games.tictactoe.models import Status
from core.games.transform import GameStateDataSerializer, GameTurnDataSerializer
from core.games.utils import infinite_cycle
from core.types import GameState


class TicTacToeGameStateDataSerializer(GameStateDataSerializer):
    """TicTacToe game state serializer"""

    @staticmethod
    def load(data: GameStateDto, **kwargs) -> Game:
        """Deserialize game state DTO to game object"""
        game = TicTacToe(data.players)

        # shift players' loop until first player from data
        # since players is a list we save ordering
        game.next_player_loop = infinite_cycle(game.players)
        while game.toggle_next_player_turn().id != data.active_player_id:
            pass

        game.board = data.board
        game.turn = data.turn
        game.status = Status(data.status)
        return game

    @staticmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Serializer game object to game state DTO"""
        return GameStateDto(
            active_player_id=game.active_player.id,
            players=[pl.id for pl in game.players],
            board=game.board,
            status=game.status.value,
            turn=game.turn,
            winner_id=str(game.winner.id) if game.winner else None,
        ).asdict()
