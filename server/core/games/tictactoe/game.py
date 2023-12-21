"""TicTacToe game"""

import random

from typing import Any, List, Self

from core.games.exceptions import InvalidGameStateError, TurnOrderViolationError
from core.games.game import Game
from core.games.tictactoe.exceptions import CellAlreadyUsedError, InvalidTurnData
from core.games.tictactoe.models import Player, Status
from core.games.utils import infinite_cycle
from core.types import GameDataTurn

WIN_COMBOS = [
    [0, 1, 2],
    [3, 4, 5],
    [6, 7, 8],
    [0, 3, 6],
    [1, 4, 7],
    [2, 5, 8],
    [0, 4, 8],
    [2, 4, 6],
]


def get_winner_id(squares: List[Any]) -> str | None:
    """Return player's ID if game is finished"""
    for a, b, c in WIN_COMBOS:
        if squares[a] == squares[b] == squares[c]:
            return squares[a]
    return None


def validate_game_turn(game: "TicTacToe", player_id: str, turn: dict) -> None:
    """Assert player can make turn"""
    if not game.is_game_in_progress:
        raise InvalidGameStateError
    player = game.active_player
    if not player or player.id != player_id:
        raise TurnOrderViolationError
    index = turn.get("index")
    if index is None or 0 < index > len(game.board):
        raise InvalidTurnData
    if game.board[index]:
        raise CellAlreadyUsedError


class TicTacToe(Game):
    """TicTacToe Game class"""

    def __init__(self: Self, player_ids: List[str]) -> None:
        """Init game class"""
        assert len(player_ids), "No players found."
        self.players = [Player(p_id) for p_id in player_ids]
        self.turn = 0
        self.status = Status.CREATED
        self.next_player_loop = infinite_cycle(self.players)
        self.board: list = []
        self.active_player: Player
        self.winner: Player | None = None

    @classmethod
    def init_new_game(cls, player_ids: List[str]) -> "TicTacToe":
        """Start new game"""
        game = cls(player_ids)
        game.status = Status.IN_PROGRESS
        game.turn = 1
        # randomly peek first player
        random.shuffle(game.players)
        game.active_player = game.toggle_next_player_turn()
        game.board = [None] * 9
        return game

    def toggle_next_player_turn(self) -> Player:
        """Change first player to next"""
        self.active_player = next(self.next_player_loop)
        return self.active_player

    def make_turn(self: Self, player_id: str, turn: GameDataTurn) -> Self:
        """Player makes a turn"""
        # always run validation before apply a turn
        validate_game_turn(self, player_id, turn)
        index = turn["index"]
        player = self.active_player
        self.board[index] = player.id

        winner_id = get_winner_id(self.board)
        if winner_id:
            self.status = Status.FINISHED
            self.winner = player
        elif all(cell for cell in self.board):
            self.status = Status.DRAW

        self.toggle_next_player_turn()
        self.turn += 1
        return self

    @property
    def is_game_in_progress(self: Self) -> bool:
        """True if game is in progress"""
        return self.status == Status.IN_PROGRESS
