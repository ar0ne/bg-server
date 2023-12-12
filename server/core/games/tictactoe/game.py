"""TicTacToe game"""

import random
from typing import Any, List

from ..base import Id
from ..tictactoe.models import Board, Player, Status
from ..utils import infinite_cycle


def calculate_winner(squares) -> Id | None:
    """Return player's ID if game is finished"""
    lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ]
    for a, b, c in lines:
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

    @staticmethod
    def start_new_game(player_ids: List[Id]) -> "Game":
        """Start new game"""
        game = Game(player_ids)
        game.status = Status.IN_PROGRESS
        game.turn = 1
        # randomly peek first player
        random.shuffle(game.players)
        game.active_player = game.toggle_next_player_turn()
        game.board = Board()
        return game

    def toggle_next_player_turn(self) -> Player:
        """Change first player to next"""
        self.active_player = next(self.next_player_loop)
        return self.active_player

    def make_turn(self, player: Player, turn: Any) -> None:
        """Player makes a turn"""
        index = turn["cell"]
        # FIXME: run internal validation
        self.board[index] = player.id

        # FIXME: check game state
        winner = calculate_winner(self.board)
        if winner:
            self.status = Status.FINISHED
            # FIXME: save winner ID ?

        self.toggle_next_player_turn()
        self.turn += 1
