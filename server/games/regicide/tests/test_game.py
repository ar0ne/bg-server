"""Unit tests for game"""
import unittest

from server.games.regicide.dto import GameData
from server.games.regicide.game import Game
from server.games.regicide.models import GameState
from server.games.regicide.utils import load_data


class TestGame(unittest.TestCase):
    """Test cases for game"""

    def setUp(self) -> None:
        """Setup test cases"""
        self.user1_id = "user1"
        self.user2_id = "user2"

    def test_create_game(self) -> None:
        """Tests creating new game object"""

        with self.assertRaises(AssertionError):
            Game([])

        user_id = "user1"

        game = Game([user_id])

        self.assertEqual(user_id, game.first_player.id)
        self.assertEqual(1, len(game.players))
        self.assertEqual(0, game.turn)
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

    def test_play_cards_kill_enemy(self) -> None:
        """Tests playing cards and kill enemy"""
        dump = GameData(
            enemy_deck=[("J", "♣"), ("J", "♥")],
            discard_deck=[("5", "♥")],
            first_player_id=self.user1_id,
            players=[
                (self.user1_id, [("4", "♥")]),
                (self.user2_id, [("2", "♥")]),
            ],
            played_combos=[[("10", "♣")], [("6", "♠")]],
            state=GameState.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=4,
        )
        game = Game([self.user1_id, self.user2_id])
        load_data(game, dump)
        enemy = game.enemy_deck.peek()

        # Player kills enemy and draws 1 card from discard to tavern and should defeat next enemy
        # And enemy doesn't have immune
        game.play_cards(game.first_player, [game.first_player.hand[0]])

        self.assertEqual(GameState.PLAYING_CARDS, game.state)
        self.assertEqual(5, game.turn)
        self.assertEqual(game.first_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertNotEqual(enemy, game.enemy_deck.peek())
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(3, len(game.discard_deck))
        self.assertEqual(3, len(game.tavern_deck))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_diamond_card(self) -> None:
        """Tests playing diamond card and draw from tavern"""
        dump = GameData(
            enemy_deck=[("J", "♣")],
            discard_deck=[("5", "♥")],
            first_player_id=self.user1_id,
            players=[
                (self.user1_id, [("2", "♦")]),
                (self.user2_id, [("2", "♥")]),
            ],
            played_combos=[
                [("9", "♠")],
            ],
            state=GameState.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣"), ("3", "♥"), ("4", "♥")],
            turn=4,
        )
        game = Game([self.user1_id, self.user2_id])
        load_data(game, dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        game.play_cards(game.first_player, [game.first_player.hand[0]])

        self.assertEqual(GameState.DISCARDING_CARDS, game.state)
        self.assertEqual(5, game.turn)
        self.assertEqual(game.first_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].hand))

    def test_play_cards__game_lost_due_to_empty_hand(self) -> None:
        """Tests playing card and no cards to defeat enemy"""
        dump = GameData(
            enemy_deck=[("J", "♣")],
            discard_deck=[("5", "♥")],
            first_player_id=self.user1_id,
            players=[
                (self.user1_id, [("2", "♣")]),
                (self.user2_id, [("2", "♥")]),
            ],
            played_combos=[
                [("9", "♣")],
            ],
            state=GameState.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=4,
        )
        game = Game([self.user1_id, self.user2_id])
        load_data(game, dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        game.play_cards(game.first_player, [game.first_player.hand[0]])

        self.assertEqual(GameState.LOST, game.state)
        self.assertEqual(4, game.turn)
        self.assertEqual(game.first_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_cards__won_game(self) -> None:
        """Tests playing card and won the game"""
        dump = GameData(
            enemy_deck=[("J", "♥")],
            discard_deck=[("3", "♣")],
            first_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("4", "♣"), ("Q", "♣"), ("9", "♣")]),
            ],
            played_combos=[],
            state=GameState.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=6,
        )
        game = Game([self.user2_id, self.user1_id])
        load_data(game, dump)

        # player plays card with damage enough to defeat the enemy and won the game
        game.play_cards(game.first_player, [game.first_player.hand[1]])

        self.assertEqual(GameState.WON, game.state)
        self.assertEqual(6, game.turn)
        self.assertEqual(game.first_player.id, self.user1_id)
        self.assertEqual(0, len(game.enemy_deck))
        self.assertEqual(3, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(0, len(game.played_combos))
        self.assertEqual(0, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].hand))

    def test_play_cards__combo_from_twos(self) -> None:
        """Tests playing card combo from 2x4"""
        dump = GameData(
            enemy_deck=[("K", "♥")],
            discard_deck=[("4", "♣")],
            first_player_id=self.user1_id,
            players=[
                (self.user2_id, []),
                (self.user1_id, [("2", "♣"), ("2", "♥"), ("2", "♦"), ("2", "♠")]),
            ],
            played_combos=[[("10", "♠")]],
            state=GameState.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", "♣"), ("4", "♣")],
            turn=6,
        )
        game = Game([self.user2_id, self.user1_id])
        load_data(game, dump)

        # player plays combo from 2x4, enemy has immune to hearts
        game.play_cards(
            game.first_player,
            [
                game.first_player.hand[0],
                game.first_player.hand[1],
                game.first_player.hand[2],
                game.first_player.hand[3],
            ],
        )

        self.assertEqual(GameState.PLAYING_CARDS, game.state)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.first_player.id, self.user2_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(0, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))

    def test_play_cards__combo_with_ace(self) -> None:
        """Tests playing card combo from ace and card"""
        dump = GameData(
            enemy_deck=[("Q", "♦")],
            discard_deck=[("4", "♣")],
            first_player_id=self.user1_id,
            players=[
                (self.user2_id, [("3", "♣")]),
                (self.user1_id, [("5", "♣"), ("10", "♠"), ("K", "♦"), ("A", "♦")]),
            ],
            played_combos=[[("4", "♠")]],
            state=GameState.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("4", "♣")],
            turn=6,
        )
        game = Game([self.user2_id, self.user1_id])
        load_data(game, dump)

        # player plays combo from ace and 5, game moves to discard cards state
        game.play_cards(game.first_player, [game.first_player.hand[0], game.first_player.hand[3]])

        self.assertEqual(GameState.DISCARDING_CARDS, game.state)
        self.assertEqual(7, game.turn)
        self.assertEqual(game.first_player.id, self.user1_id)
        self.assertEqual(1, len(game.enemy_deck))
        self.assertEqual(1, len(game.discard_deck))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(2, len(game.players[1].hand))

    def test_discard_cards(self) -> None:
        """Tests discarding cards"""
        dump = GameData(
            enemy_deck=[("Q", "♦")],
            discard_deck=[("4", "♣")],
            first_player_id=self.user1_id,
            players=[
                (self.user2_id, [("3", "♣")]),
                (self.user1_id, [("10", "♠"), ("K", "♦")]),
            ],
            played_combos=[[("4", "♠")], [("5", "♣"), ("A", "♦")]],
            state=GameState.DISCARDING_CARDS.value,  # type: ignore
            tavern_deck=[("4", "♣")],
            turn=6,
        )
        game = Game([self.user2_id, self.user1_id])
        load_data(game, dump)

        game.discard_cards(game.first_player, [game.players[1].hand[1]])

        self.assertEqual(GameState.PLAYING_CARDS, game.state)
        self.assertEqual(game.first_player.id, self.user2_id)
        self.assertEqual(2, len(game.discard_deck))
        self.assertEqual(2, len(game.played_combos))
        self.assertEqual(1, len(game.tavern_deck))
        self.assertEqual(6, game.turn)
        self.assertEqual(1, len(game.players[0].hand))
        self.assertEqual(1, len(game.players[1].hand))
