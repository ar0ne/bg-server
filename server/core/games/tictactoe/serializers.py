"""TicTacToe converters"""

from core.games.tictactoe.dto import GameStateDto
from core.games.tictactoe.game import TicTacToe
from core.games.tictactoe.models import Status
from core.games.utils import infinite_cycle
from core.types import GameState


class TicTacToeGameStateDataSerializer:
    """TicTacToe game state serializer"""

    @staticmethod
    def loads(data: GameStateDto, **kwargs) -> TicTacToe:
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
    def dumps(game: TicTacToe, **kwargs) -> GameState:
        """Serializer game object to game state DTO"""
        return GameStateDto(
            active_player_id=game.active_player.id,
            players=[pl.id for pl in game.players],
            board=game.board,
            status=game.status.value,
            turn=game.turn,
            winner_id=str(game.winner.id) if game.winner else None,
        ).asdict()
