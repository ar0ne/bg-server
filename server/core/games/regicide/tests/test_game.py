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
from core.games.regicide.game import Game
from core.games.regicide.models import Status
from core.games.regicide.serializers import RegicideGameStateDataSerializer


class TestGame(TestCase):
    """Test cases for game"""

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

    def test_start_new_game(self) -> None:
        """Tests starting new game"""

        hand_size = 7

        game = Game.start_new_game([self.user1_id, self.user2_id])

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
            enemy_deck=[("J", "♣"), ("J", "♥")],
            discard_deck=[("5", "♥")],
            active_player_id=self.user1_id,
            players=[
                (self.user1_id, [("4", "♥")]),
                (self.user2_id, [("2", "♥")]),
            ],
            played_combos=[[("10", "♣")], [("6", "♠")]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=4,
        )
        game = self.game_state_serializer.load(dump)

        enemy = game.enemy_deck.peek()

        # Player kills enemy and draws 1 card from discard to tavern and should defeat next enemy
        # And enemy doesn't have immune
        turn = {"cards": [("4", "♥")]}
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
        dump = GameStateDto(
            enemy_deck=[("J", "♣")],
            discard_deck=[("5", "♥")],
            active_player_id=self.user1_id,
            players=[
                (self.user1_id, [("2", "♦")]),
                (self.user2_id, [("2", "♥")]),
            ],
            played_combos=[
                [("9", "♠")],
            ],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣"), ("3", "♥"), ("4", "♥")],
            turn=4,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        turn = {"cards": [("2", "♦")]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.DISCARDING_CARDS, game.status)
        self.assertEqual(5, game.turn)
        self.assertEqual(game.active_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].hand))

    def test_play_cards__game_lost_due_to_empty_hand(self) -> None:
        """Tests playing card and no cards to defeat enemy"""
        dump = GameStateDto(
            enemy_deck=[("J", "♣")],
            discard_deck=[("5", "♥")],
            active_player_id=self.user1_id,
            players=[
                (self.user1_id, [("2", "♣")]),
                (self.user2_id, [("2", "♥")]),
            ],
            played_combos=[
                [("9", "♣")],
            ],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=4,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        turn = {"cards": [("2", "♣")]}
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
            enemy_deck=[("J", "♥")],
            discard_deck=[("3", "♣")],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("4", "♣"), ("9", "♣"), ("Q", "♣")]),
            ],
            played_combos=[],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # player plays card with damage enough to defeat the enemy and won the game
        turn = {"cards": [("Q", "♣")]}
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
            enemy_deck=[("Q", "♥")],
            discard_deck=[("4", "♣")],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("2", "♣"), ("2", "♥"), ("2", "♦"), ("2", "♠")]),
            ],
            played_combos=[[("10", "♠")]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", "♣"), ("4", "♣")],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from 2x4, enemy has immune to hearts
        turn = {"cards": [("2", "♣"), ("2", "♥"), ("2", "♦"), ("2", "♠")]}
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
            enemy_deck=[("Q", "♥")],
            discard_deck=[("4", "♣")],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("10", "♥")]),
            ],
            played_combos=[[("10", "♠")]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", "♣"), ("4", "♣")],
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
            enemy_deck=[("Q", "♦")],
            discard_deck=[("4", "♣")],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, [("3", "♣")]),
                (self.user1_id, [("5", "♣"), ("10", "♠"), ("K", "♦"), ("A", "♦")]),
            ],
            played_combos=[[("4", "♠")]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("4", "♣")],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)

        # player plays combo from ace and 5, game moves to discard cards state
        turn = {"cards": [("5", "♣"), ("A", "♦")]}
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

    def test_play_cards__invalid_turn(self) -> None:
        """Tests playing card combo :: invalid turn"""
        five_clubs = ("5", "♣")
        five_diamonds = ("5", "♦")
        five_spades = ("5", "♠")
        six_clubs = ("6", "♣")
        six_diamonds = ("6", "♦")
        ten_spades = ("10", "♠")
        jack_diamonds = ("J", "♦")
        ace_diamonds = ("A", "♦")
        dump = GameStateDto(
            enemy_deck=[("Q", "♦")],
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
            Game.make_turn(game, game.active_player.id, [("♣", "5")])

        invalid_combos = [
            ([("A", "♣")], CardDoesNotBelongsToPlayerError),
            ([ace_diamonds, ("2", "♦")], CardDoesNotBelongsToPlayerError),
            ([("♣", "5")], InvalidCardDataError),
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
            enemy_deck=[("Q", "♦")],
            discard_deck=[("4", "♣")],
            active_player_id=self.user1_id,
            players=[
                (self.user2_id, [("3", "♣")]),
                (self.user1_id, [("10", "♠"), ("K", "♦")]),
            ],
            played_combos=[[("4", "♠")], [("5", "♣"), ("A", "♦")]],
            status=Status.DISCARDING_CARDS.value,  # type: ignore
            tavern_deck=[("4", "♣")],
            turn=6,
        )
        game = self.game_state_serializer.load(dump)
        turn = {"cards": [("K", "♦")]}
        game = Game.make_turn(game, game.active_player.id, turn)

        self.assertEqual(Status.PLAYING_CARDS, game.status)
        self.assertEqual(game.active_player.id, self.user2_id)
        self.assertEqual(2, len(game.discard_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(game.turn, dump.turn + 1)
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))
