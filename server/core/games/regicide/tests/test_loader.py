"""Tests utilities"""
from unittest import TestCase

from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Game
from core.games.regicide.internal import RegicideGameLoader
from core.games.regicide.models import Card, CardRank, Deck, GameState, Suit


class TestGameLoader(TestCase):
    """unit tests for game loader"""

    @classmethod
    def setUpClass(cls) -> None:
        """Setup test class"""
        cls.loader = RegicideGameLoader()

    def test_upload_game_state(self) -> None:
        """Tests dumping (upload) game state"""

        user_id = "user_id"
        game = Game([user_id])
        player = game.first_player
        card = Card(suit=Suit.HEARTS, rank=CardRank.FOUR)
        player.hand = [card]
        game.enemy_deck = Deck([Card(suit=Suit.SPADES, rank=CardRank.JACK)])
        game.tavern_deck = Deck([Card(suit=Suit.CLUBS, rank=CardRank.TWO)])
        game.played_combos = [
            [Card(suit=Suit.CLUBS, rank=CardRank.FIVE), Card(suit=Suit.HEARTS, rank=CardRank.ACE)],
            [Card(suit=Suit.SPADES, rank=CardRank.THREE)],
        ]
        game.discard_deck = Deck([Card(suit=Suit.DIAMONDS, rank=CardRank.NINE)])
        game.state = GameState.DISCARDING_CARDS
        game.turn = 5

        dump = self.loader.upload(game)

        self.assertEqual([("J", "♠")], dump.enemy_deck)
        self.assertEqual([("2", "♣")], dump.tavern_deck)
        self.assertEqual(dump.first_player_id, user_id)
        self.assertEqual([(user_id, [("4", "♥")])], dump.players)
        self.assertEqual([[("5", "♣"), ("A", "♥")], [("3", "♠")]], dump.played_combos)
        self.assertEqual([("9", "♦")], dump.discard_deck)
        self.assertEqual(dump.turn, 5)
        self.assertEqual(dump.state, GameState.DISCARDING_CARDS.value)

    def test_load_data(self) -> None:
        """Tests loading game data"""
        user1_id = "user1_id"
        user2_id = "user2_id"
        dump = GameStateDto(
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
        game = self.loader.load(dump)

        self.assertEqual(20, game.turn)
        self.assertEqual(GameState.DISCARDING_CARDS, game.state)
        self.assertEqual(user2_id, game.first_player.id)
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(CardRank.TWO, game.tavern_deck.cards[0].rank)
        self.assertEqual(Suit.CLUBS, game.tavern_deck.cards[0].suit)
        self.assertEqual(2, len(game.players))
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(CardRank.JACK, game.enemy_deck.cards[0].rank)
        self.assertEqual(Suit.SPADES, game.enemy_deck.cards[0].suit)
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(CardRank.NINE, game.discard_deck.cards[0].rank)
        self.assertEqual(Suit.DIAMONDS, game.discard_deck.cards[0].suit)
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(Suit.CLUBS, game.played_combos[0][0].suit)
        self.assertEqual(CardRank.FIVE, game.played_combos[0][0].rank)
        self.assertEqual(Suit.HEARTS, game.played_combos[0][1].suit)
        self.assertEqual(CardRank.ACE, game.played_combos[0][1].rank)
        self.assertEqual(Suit.SPADES, game.played_combos[1][0].suit)
        self.assertEqual(CardRank.THREE, game.played_combos[1][0].rank)

        # TODO: check players' hands