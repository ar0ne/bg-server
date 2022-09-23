"""Tests utilities"""
from unittest import TestCase

from server.app.games.regicide.game import Game
from server.app.games.regicide.models import Suit, Card, Deck, GameState
from server.app.games.regicide.utils import dump_data


class TestUtilities(TestCase):
    """unit tests for utilities"""

    def test_dump_data(self) -> None:
        """Tests dumping game data"""

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

        dump = dump_data(game)

        self.assertEqual([("J", "♠")], dump.enemy_deck)
        self.assertEqual([("2", "♣")], dump.tavern_deck)
        self.assertEqual(user_id, dump.first_player_id)
        self.assertEqual([(user_id, [("4", "♥")])], dump.players)
        self.assertEqual([[("5", "♣"), ("A", "♥")], [("3", "♠")]], dump.played_cards)
        self.assertEqual([("9", "♦")], dump.discard_deck)
        self.assertEqual(5, dump.turn)
        self.assertEqual(GameState.DISCARDING_CARDS.value, dump.state)
