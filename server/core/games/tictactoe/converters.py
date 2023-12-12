"""TicTacToe converters"""

from core.games.tictactoe.dto import GameStateDto, GameTurnDataDto
from core.games.tictactoe.game import Game
from core.games.tictactoe.models import Board, Status
from core.games.transform import GameStateDataConverter, GameTurnDataConverter
from core.games.utils import infinite_cycle

from ..base import GameState


class TicTacToeGameTurnDataConverter(GameTurnDataConverter):
    """TicTacToe Game turn data converter"""

    @staticmethod
    def dump(game: Game, **kwargs) -> GameTurnDataDto:
        """Dump game turn data for player into the object"""

        return GameTurnDataDto(
            active_player_id=game.active_player.id,
            # board=game.board,
            player_id=player_id or "",
            status=game.status.value,
            turn=game.turn,
        )


class TicTacToeGameStateDataConverter(GameStateDataConverter):
    """TicTacToe game state converter"""

    @staticmethod
    def load(data: GameStateDto, **kwargs) -> Game:
        """Load game state to game instance"""
        game = Game(data.players)

        # shift players' loop until first player from data
        game.next_player_loop = infinite_cycle(game.players)
        while game.toggle_next_player_turn().id != data.active_player_id:
            pass
        game.board = Board(data.board)
        game.turn = data.turn
        game.status = Status(data.status)
        return game

    @staticmethod
    def dump(game: Game, **kwargs) -> GameState:
        """Dump game state into the DTO"""
        return GameStateDto(
            active_player_id=game.active_player.id,
            players=[pl.id for pl in game.players],
            board=game.board.items,
            status=game.status.value,
            turn=game.turn,
        )
