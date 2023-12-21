"""Unit tests for game"""
from unittest import TestCase

from core.games.regicide.dto import GameStateDto
from core.games.regicide.exceptions import (
    CardDoesNotBelongsToPlayerError,
    InvalidCardDataError,
    InvalidPairComboError,
    InvalidTurnDataError,
    MaxComboSizeExceededError,
)
from core.games.regicide.game import Regicide as Game
from core.games.regicide.models import Status, Suit
from core.games.regicide.serializers import RegicideGameStateDataSerializer
from core.games.regicide.utils import to_flat_hand
from core.games.transform import GameStateDataSerializer
from core.types import GameData

CLUBS = Suit.CLUBS.value
HEARTS = Suit.HEARTS.value
SPADES = Suit.SPADES.value
DIAMONDS = Suit.DIAMONDS.value


class TestGame(TestCase):
    """Test cases for game"""

    user1_id = ""
    user2_id = ""
    game_state_serializer: GameStateDataSerializer = None

    @classmethod
    def setUpClass(cls) -> None:
        """Setup test cases"""
        cls.user1_id = "user1"
        cls.user2_id = "user2"
        cls.game_state_serializer = RegicideGameStateDataSerializer()

    def test_create_game(self) -> None:
        """Tests creating new game object"""

        with self.assertRaises(AssertionError):
            Game([])

        game = Game([self.user1_id])

        self.assertIsNone(game.active_player)
        self.assertEqual(1, len(game.players))
        self.assertEqual(0, game.turn)
        self.assertEqual(0, len(game.discard_deck))
        self.assertEqual(0, len(game.tavern_deck))
        self.assertEqual(0, len(game.enemy_deck))
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(Status.CREATED, game.status)

    def test_init_new_game(self) -> None:
        """Tests initializing new game"""

        hand_size = 7

        game = Game.init_new_game([self.user1_id, self.user2_id])

        self.assertEqual(Status.PLAYING_CARDS, game.status)
        self.assertEqual(1, game.turn)
        self.assertEqual(2, len(game.players))
        self.assertTrue(game.active_player in game.players)
        self.assertEqual(0, len(game.discard_deck))
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(12, len(game.enemy_deck))
        self.assertEqual(40 - 2 * hand_size, len(game.tavern_deck))
        self.assertTrue(all(len(player.hand) == hand_size for player in game.players))

    def test_play_cards_kill_enemy(self) -> None:
        """Tests playing cards and kill enemy"""
        dump = GameStateDto(
            enemy_deck=[("J", CLUBS), ("J", HEARTS)],
            discard_deck=[("5", HEARTS)],
            active_player_id=self.user1_id,
            players=[
                (self.user1_id, [("4", HEARTS)]),
                (self.user2_id, [("2", HEARTS)]),
            ],
            played_combos=[[("10", CLUBS)], [("6", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", CLUBS)],
            turn=4,
        )
        game = self.game_state_serializer.load(dump)

        enemy = game.enemy_deck.peek()

        # Player kills enemy and draws 1 card from discard to tavern and should defeat next enemy
        # And enemy doesn't have immune
        turn = {"cards": [("4", HEARTS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.PLAYING_CARDS, game.status)
        self.assertEqual(5, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertNotEqual(enemy, game.enemy_deck.peek())
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(3, len(game.discard_deck))
        self.assertEqual(3, len(game.tavern_deck))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_diamond_card(self) -> None:
        """Tests playing diamond card and draw from tavern"""
        user_1_hand = [("5", DIAMONDS)]
        user_2_hand = [
            ("2", SPADES),
            ("2", CLUBS),
            ("2", HEARTS),
            ("2", DIAMONDS),
            ("3", SPADES),
            ("3", HEARTS),
        ]
        dump = GameStateDto(
            enemy_deck=[("J", CLUBS)],
            discard_deck=[("5", HEARTS)],
            active_player_id=self.user1_id,
            players=[
                (self.user1_id, user_1_hand),
                (self.user2_id, user_2_hand),
            ],
            played_combos=[
                [("9", SPADES)],
            ],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("8", CLUBS), ("8", HEARTS), ("9", HEARTS), ("9", DIAMONDS)],
            turn=4,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        turn = {"cards": [("5", DIAMONDS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.DISCARDING_CARDS, game.status)
        self.assertEqual(5, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(0, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(3, len(game.players[0].hand))
        self.assertEqual(7, len(game.players[1].hand))
        self.assertListEqual(
            [("8", CLUBS), ("9", HEARTS), ("9", DIAMONDS)], to_flat_hand(game.players[0].hand)
        )
        self.assertListEqual(user_2_hand + [("8", HEARTS)], to_flat_hand(game.players[1].hand))

    def test_play_cards__game_lost_due_to_empty_hand(self) -> None:
        """Tests playing card and no cards to defeat enemy"""
        dump = GameStateDto(
            enemy_deck=[("J", CLUBS)],
            discard_deck=[("5", HEARTS)],
            active_player_id=self.user1_id,
            players=[
                (self.user1_id, [("2", CLUBS)]),
                (self.user2_id, [("2", HEARTS)]),
            ],
            played_combos=[
                [("9", CLUBS)],
            ],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", CLUBS)],
            turn=4,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        turn = {"cards": [("2", CLUBS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.LOST, game.status)
        self.assertEqual(5, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_cards__won_game(self) -> None:
        """Tests playing card and won the game"""
        dump = GameStateDto(
            enemy_deck=[("J", HEARTS)],
            discard_deck=[("3", CLUBS)],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("4", CLUBS), ("9", CLUBS), ("Q", CLUBS)]),
            ],
            played_combos=[],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", CLUBS)],
            turn=6,
        )
        game: Regicide = self.game_state_serializer.load(dump)

        # player plays card with damage enough to defeat the enemy and won the game
        turn = {"cards": [("Q", CLUBS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(game.status, Status.WON)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(0, len(game.enemy_deck))
        self.assertEqual(3, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].hand))

    def test_play_cards__combo_from_twos(self) -> None:
        """Tests playing card combo from 2x4"""
        dump = GameStateDto(
            enemy_deck=[("Q", HEARTS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("2", CLUBS), ("2", HEARTS), ("2", DIAMONDS), ("2", SPADES)]),
            ],
            played_combos=[[("10", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", CLUBS), ("4", CLUBS)],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from 2x4, enemy has immune to hearts
        turn = {"cards": [("2", CLUBS), ("2", HEARTS), ("2", DIAMONDS), ("2", SPADES)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.PLAYING_CARDS, game.status)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.active_player.id, self.user2_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(0, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_cards__skip_playing_cards(self) -> None:
        """Tests skipping playing card combo"""
        dump = GameStateDto(
            enemy_deck=[("Q", HEARTS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("10", HEARTS)]),
            ],
            played_combos=[[("10", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", CLUBS), ("4", CLUBS)],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # empty cards means player skipped playing cards and want to discard if needed
        turn = {"cards": []}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.DISCARDING_CARDS, game.status)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(2, len(game.tavern_deck))
        self.assertEqual(1, len(game.played_combos))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_cards__combo_with_ace(self) -> None:
        """Tests playing card combo from ace and card"""
        dump = GameStateDto(
            enemy_deck=[("Q", DIAMONDS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, [("3", CLUBS)]),
                (self.user1_id, [("5", CLUBS), ("10", SPADES), ("K", DIAMONDS), ("A", DIAMONDS)]),
            ],
            played_combos=[[("4", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("4", CLUBS)],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from ace and 5, game moves to discard cards state
        turn = {"cards": [("5", CLUBS), ("A", DIAMONDS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.DISCARDING_CARDS, game.status)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].hand))

    def test_play_cards__combo_with_ace_and_hearts(self) -> None:
        """Tests playing card combo from ace and card"""
        dump = GameStateDto(
            enemy_deck=[("Q", DIAMONDS)],
            discard_deck=[
                ("3", CLUBS),
                ("4", CLUBS),
                ("10", SPADES),
                ("K", DIAMONDS),
                ("A", HEARTS),
                ("2", HEARTS),
                ("2", CLUBS),
            ],
            active_player_id=self.user1_id,
            players=[
                (
                    self.user1_id,
                    [("4", HEARTS), ("10", HEARTS), ("J", HEARTS), ("Q", HEARTS), ("A", DIAMONDS)],
                ),
            ],
            played_combos=[[("4", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from ace and 4 (power - 5), game moves to discard cards state
        turn = {"cards": [("4", HEARTS), ("A", DIAMONDS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.DISCARDING_CARDS, game.status)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(2, len(game.discard_deck))
        self.assertEqual(5, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(3, len(game.players[0].hand))

    def test_play_cards__invalid_turn(self) -> None:
        """Tests playing card combo :: invalid turn"""
        five_clubs = ("5", CLUBS)
        five_diamonds = ("5", DIAMONDS)
        five_spades = ("5", SPADES)
        six_clubs = ("6", CLUBS)
        six_diamonds = ("6", DIAMONDS)
        ten_spades = ("10", SPADES)
        jack_diamonds = ("J", DIAMONDS)
        ace_diamonds = ("A", DIAMONDS)
        dump = GameStateDto(
            enemy_deck=[("Q", DIAMONDS)],
            discard_deck=[],
            active_player_id=self.user1_id,
            players=[
                (
                    self.user1_id,
                    [
                        five_clubs,
                        five_diamonds,
                        five_spades,
                        six_clubs,
                        six_diamonds,
                        ten_spades,
                        jack_diamonds,
                        ace_diamonds,
                    ],
                ),
            ],
            played_combos=[],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[],
            turn=2,
        )
        game = self.game_state_serializer.load(dump)

        with self.assertRaises(InvalidTurnDataError):
            Game.make_turn(game, game.active_player.id, None)
        with self.assertRaises(InvalidTurnDataError):
            Game.make_turn(game, game.active_player.id, {})
        with self.assertRaises(InvalidTurnDataError):
            Game.make_turn(game, game.active_player.id, [(CLUBS, "5")])

        invalid_combos = [
            ([("A", CLUBS)], CardDoesNotBelongsToPlayerError),
            ([ace_diamonds, ("2", DIAMONDS)], CardDoesNotBelongsToPlayerError),
            ([(CLUBS, "5")], InvalidCardDataError),
            ([ten_spades, jack_diamonds, ace_diamonds], MaxComboSizeExceededError),
            ([ten_spades, jack_diamonds], InvalidPairComboError),
            ([six_diamonds, six_clubs], InvalidPairComboError),
            ([five_clubs, five_diamonds, five_spades], InvalidPairComboError),
        ]
        for combo, exc in invalid_combos:
            with self.subTest(combo=combo, exc=exc):
                with self.assertRaises(exc):
                    Game.make_turn(game, game.active_player.id, {"cards": combo})

    def test_discard_cards(self) -> None:
        """Tests discarding cards"""
        dump = GameStateDto(
            enemy_deck=[("Q", DIAMONDS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, [("3", CLUBS)]),
                (self.user1_id, [("10", SPADES), ("K", DIAMONDS)]),
            ],
            played_combos=[[("4", SPADES)], [("5", CLUBS), ("A", DIAMONDS)]],
            status=Status.DISCARDING_CARDS.value,  # type: ignore
            tavern_deck=[("4", CLUBS)],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)
        turn = {"cards": [("K", DIAMONDS)]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.PLAYING_CARDS, game.status)
        self.assertEqual(game.active_player.id, self.user2_id)
        self.assertEqual(2, len(game.discard_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(game.turn, dump.turn + 1)
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))
