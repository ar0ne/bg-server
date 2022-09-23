"""Tests utilities"""
from unittest import TestCase

from server.app.games.regicide.dto import GameData
from server.app.games.regicide.game import Game
from server.app.games.regicide.models import Suit, Card, Deck, GameState
from server.app.games.regicide.utils import dump_data, load_data


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
        game.played_combos = [
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
        self.assertEqual([[("5", "♣"), ("A", "♥")], [("3", "♠")]], dump.played_combos)
        self.assertEqual([("9", "♦")], dump.discard_deck)
        self.assertEqual(5, dump.turn)
        self.assertEqual("discarding_cards", dump.state)

    def test_load_data(self) -> None:
        """Tests loading game data"""
        user1_id = "user1_id"
        user2_id = "user2_id"
        dump = GameData(
            enemy_deck=[("J", "♠")],
            discard_deck=[("9", "♦")],
            first_player_id=user2_id,
            players=[
                (user1_id, [("4", "♥")]),
                (user2_id, [("2", "♥")]),
            ],
            played_combos=[[("5", "♣"), ("A", "♥")], [("3", "♠")]],
            state="discarding_cards",  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=20,
        )
        game = Game([user1_id, user2_id])

        load_data(game, dump)

        self.assertEqual(20, game.turn)
        self.assertEqual(GameState.DISCARDING_CARDS, game.state)
        self.assertEqual(user2_id, game.first_player.id)
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(Card.TWO, game.tavern_deck.cards[0].rank)
        self.assertEqual(Suit.CLUBS, game.tavern_deck.cards[0].suit)
        # self.assertEqual(2, )