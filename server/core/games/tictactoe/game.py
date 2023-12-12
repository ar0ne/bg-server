"""TicTacToe game"""

import random
from typing import List

from ..base import Id
from ..tictactoe.models import Board, GameState, Player
from ..utils import infinite_cycle


class Game:
    """TicTacToe Game class"""

    def __init__(self, player_ids: List[Id]) -> None:
        """Init game class"""
        assert len(player_ids), "No players found."
        self.players = [Player(p_id) for p_id in player_ids]
        self.turn = 0
        self.size = 3  # FIXME: do it configurable?
        self.state = GameState.CREATED

    @staticmethod
    def start_new_game(player_ids: List[Id]) -> "Game":
        """Start new game"""
        game = Game(player_ids)
        game.state = GameState.IN_PROGRESS
        game.turn = 1
        # randomly peek first player
        random.shuffle(game.players)
        game.next_player_loop = infinite_cycle(game.players)
        game.active_player = game.toggle_next_player_turn()
        game.board = Board(game.size)
        return game

    def toggle_next_player_turn(self) -> Player:
        """Change first player to next"""
        self.active_player = next(self.next_player_loop)
        return self.active_player
