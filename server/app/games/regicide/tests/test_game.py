"""Unit tests for game"""
import unittest

from server.app.games.regicide.game import Game
from server.app.games.regicide.models import GameState, Card, Suit, Deck


class TestGame(unittest.TestCase):
    """Test cases for game"""

    def test_create_game(self) -> None:
        """Tests creating new game object"""

        with self.assertRaises(AssertionError):
            Game([])

        user_id = "user1"

        game = Game([user_id])

        self.assertEqual(user_id, game.first_player.id)
        self.assertEqual(1, len(game.players))
        self.assertEqual(1, game.turn)
        self.assertEqual(0, len(game.discard_deck))
        self.assertEqual(0, len(game.tavern_deck))
        self.assertEqual(0, len(game.enemy_deck))
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(GameState.CREATED, game.state)

    def test_start_new_game(self) -> None:
        """Tests starting new game"""

        user1_id = "user1"
        user2_id = "user2"
        hand_size = 7

        game = Game([user1_id, user2_id])
        game.start_new_game()

        self.assertEqual(GameState.PLAYING_CARDS, game.state)
        self.assertEqual(1, game.turn)
        self.assertEqual(2, len(game.players))
        self.assertTrue(game.first_player in game.players)
        self.assertEqual(0, len(game.discard_deck))
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(12, len(game.enemy_deck))
        self.assertEqual(40 - 2 * hand_size, len(game.tavern_deck))
        self.assertTrue(all(len(player.hand) == hand_size for player in game.players))
