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
        self.assertEqual(0, len(game.played_cards))
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
        self.assertEqual(0, len(game.played_cards))
        self.assertEqual(12, len(game.enemy_deck))
        self.assertEqual(40 - 2 * hand_size, len(game.tavern_deck))
        self.assertTrue(all(len(player.hand) == hand_size for player in game.players))

    def test_dump_data(self) -> None:
        """Tests dumping data"""

        user_id = "user_id"
        game = Game([user_id])
        player = game.first_player
        card = Card(suit=Suit.HEARTS, rank=Card.FOUR)
        player.hand = [card]
        game.enemy_deck = Deck([Card(suit=Suit.SPADES, rank=Card.JACK)])
        game.tavern_deck = Deck([Card(suit=Suit.CLUBS, rank=Card.TWO)])
        game.played_cards = [
            [Card(suit=Suit.CLUBS, rank=Card.FIVE), Card(suit=Suit.HEARTS, rank=Card.ACE)],
            [Card(suit=Suit.SPADES, rank=Card.THREE)],
        ]
        game.discard_deck = Deck([Card(suit=Suit.DIAMONDS, rank=Card.NINE)])
        game.state = GameState.DISCARDING_CARDS
        game.turn = 5

        dump = game.dump()

        self.assertEqual([("J", "♠")], dump.enemy_deck)
        self.assertEqual([("2", "♣")], dump.tavern_deck)
        self.assertEqual(user_id, dump.first_player_id)
        self.assertEqual([(user_id, [("4", "♥")])], dump.players)
        self.assertEqual([[("5", "♣"), ("A", "♥")], [("3", "♠")]], dump.played_cards)
        self.assertEqual([("9", "♦")], dump.discard_deck)
        self.assertEqual(5, dump.turn)
        self.assertEqual(GameState.DISCARDING_CARDS.value, dump.state)
