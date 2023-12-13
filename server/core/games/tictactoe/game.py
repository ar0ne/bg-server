"""TicTacToe game"""

import random
from typing import Any, List

from ..base import Id
from ..exceptions import InvalidGameStateError, TurnOrderViolationError
from ..tictactoe.models import Player, Status
from ..utils import infinite_cycle

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


def get_winner_id(squares) -> Id | None:
    """Return player's ID if game is finished"""
    for a, b, c in WIN_COMBOS:
        if squares[a] == squares[b] == squares[c]:
            return squares[a]
    return None


class Game:
    """TicTacToe Game class"""

    def __init__(self, player_ids: List[Id]) -> None:
        """Init game class"""
        assert len(player_ids), "No players found."
        self.players = [Player(p_id) for p_id in player_ids]
        self.turn = 0
        self.status = Status.CREATED
        self.next_player_loop = infinite_cycle(self.players)
        self.board = None
        self.winner = None

    @staticmethod
    def start_new_game(player_ids: List[Id]) -> "Game":
        """Start new game"""
        game = Game(player_ids)
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

    def make_turn(self, player: Player, turn: dict) -> None:
        """Player makes a turn"""
        self._assert_can_make_turn(player, turn)
        index = turn["index"]
        self.board[index] = player.id

        winner_id = get_winner_id(self.board)
        if winner_id:
            self.status = Status.FINISHED
            self.winner = player if winner_id == player.id else Player(winner_id)

        self.toggle_next_player_turn()
        self.turn += 1

    def _assert_can_make_turn(self, player: Player, turn: dict) -> None:
        """Assert player can make turn"""
        if not self.is_game_in_progress:
            raise InvalidGameStateError
        if player not in self.players:
            raise Exception  # FIXME
        if player is not self.active_player:
            raise TurnOrderViolationError
        index = turn.get("index")
        if index is None or 0 < index > len(self.board):
            raise Exception  # FIXME
        if self.board[index]:
            raise Exception  # FIXME

    @property
    def is_game_in_progress(self) -> bool:
        """True if game is in progress"""
        return self.status == Status.IN_PROGRESS
