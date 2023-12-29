# mypy: disable-error-code=attr-defined
"""Unit tests for game"""
import pytest

from core.games.regicide.dto import GameStateDto
from core.games.regicide.exceptions import (
    CardDoesNotBelongsToPlayerError,
    InvalidCardDataError,
    InvalidPairComboError,
    InvalidTurnDataError,
    MaxComboSizeExceededError,
)
from core.games.regicide.game import Regicide
from core.games.regicide.models import Status, Suit
from core.games.regicide.serializers import RegicideGameStateDataSerializer
from core.games.regicide.utils import to_flat_hand
from core.games.serializers import GameStateDataSerializer
from core.types import GameData

CLUBS = Suit.CLUBS.value
HEARTS = Suit.HEARTS.value
SPADES = Suit.SPADES.value
DIAMONDS = Suit.DIAMONDS.value


@pytest.fixture
def serializer():
    return RegicideGameStateDataSerializer()


USER1_ID = "user1"
USER2_ID = "user2"


class TestRegicideGame:
    """Test cases for game"""

    def test_create_game(self) -> None:
        """Tests creating new game object"""

        with pytest.raises(AssertionError):
            Regicide([])

        game = Regicide([USER1_ID])

        assert 1 == len(game.players)
        assert 0 == game.turn
        assert 0 == len(game.discard_deck)
        assert 0 == len(game.tavern_deck)
        assert 0 == len(game.enemy_deck)
        assert 0 == len(game.played_combos)
        assert Status.CREATED == game.status

    def test_init_new_game(self) -> None:
        """Tests initializing new game"""

        hand_size = 7

        game = Regicide.init_new_game([USER1_ID, USER2_ID])

        assert Status.PLAYING_CARDS == game.status
        assert 1 == game.turn
        assert 2 == len(game.players)
        assert game.active_player in game.players
        assert 0 == len(game.discard_deck)
        assert 0 == len(game.played_combos)
        assert 12 == len(game.enemy_deck)
        assert 40 - 2 * hand_size == len(game.tavern_deck)
        assert all(len(player.hand) == hand_size for player in game.players)

    def test_play_cards_kill_enemy(self, serializer: GameStateDataSerializer) -> None:
        """Tests playing cards and kill enemy"""
        dump = GameStateDto(
            enemy_deck=[("J", CLUBS), ("J", HEARTS)],
            discard_deck=[("5", HEARTS)],
            active_player_id=USER1_ID,
            players=[
                (USER1_ID, [("4", HEARTS)]),
                (USER2_ID, [("2", HEARTS)]),
            ],
            played_combos=[[("10", CLUBS)], [("6", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", CLUBS)],
            turn=4,
        )
        game = serializer.loads(dump)

        enemy = game.enemy_deck.peek()

        # Player kills enemy and draws 1 card from discard to tavern and should defeat next enemy
        # And enemy doesn't have immune
        turn = {"cards": [("4", HEARTS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.PLAYING_CARDS == game.status
        assert 5 == game.turn
        assert game.active_player.id == USER1_ID
        assert 1 == len(game.enemy_deck)
        assert enemy != game.enemy_deck.peek()
        assert 0 == len(game.played_combos)
        assert 3 == len(game.discard_deck)
        assert 3 == len(game.tavern_deck)
        assert 0 == len(game.players[0].hand)
        assert 1 == len(game.players[1].hand)

    def test_play_diamond_card(self, serializer: GameStateDataSerializer) -> None:
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
            active_player_id=USER1_ID,
            players=[
                (USER1_ID, user_1_hand),
                (USER2_ID, user_2_hand),
            ],
            played_combos=[
                [("9", SPADES)],
            ],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("8", CLUBS), ("8", HEARTS), ("9", HEARTS), ("9", DIAMONDS)],
            turn=4,
        )
        game = serializer.loads(dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        turn = {"cards": [("5", DIAMONDS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.DISCARDING_CARDS == game.status
        assert 5 == game.turn
        assert game.active_player.id == USER1_ID
        assert 1 == len(game.enemy_deck)
        assert 1 == len(game.discard_deck)
        assert 0 == len(game.tavern_deck)
        assert 2 == len(game.played_combos)
        assert 3 == len(game.players[0].hand)
        assert 7 == len(game.players[1].hand)
        assert [("8", CLUBS), ("9", HEARTS), ("9", DIAMONDS)] == to_flat_hand(game.players[0].hand)
        assert user_2_hand + [("8", HEARTS)] == to_flat_hand(game.players[1].hand)

    def test_play_cards__game_lost_due_to_empty_hand(
        self, serializer: GameStateDataSerializer
    ) -> None:
        """Tests playing card and no cards to defeat enemy"""
        dump = GameStateDto(
            enemy_deck=[("J", CLUBS)],
            discard_deck=[("5", HEARTS)],
            active_player_id=USER1_ID,
            players=[
                (USER1_ID, [("2", CLUBS)]),
                (USER2_ID, [("2", HEARTS)]),
            ],
            played_combos=[
                [("9", CLUBS)],
            ],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", CLUBS)],
            turn=4,
        )
        game = serializer.loads(dump)

        # player plays combo from diamond card and draws new card. Then game moves to discard
        # cards state
        turn = {"cards": [("2", CLUBS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.LOST == game.status
        assert 5 == game.turn
        assert game.active_player.id == USER1_ID
        assert 1 == len(game.enemy_deck)
        assert 1 == len(game.discard_deck)
        assert 1 == len(game.tavern_deck)
        assert 2 == len(game.played_combos)
        assert 0 == len(game.players[0].hand)
        assert 1 == len(game.players[1].hand)

    def test_play_cards__won_game(self, serializer: GameStateDataSerializer) -> None:
        """Tests playing card and won the game"""
        dump = GameStateDto(
            enemy_deck=[("J", HEARTS)],
            discard_deck=[("3", CLUBS)],
            active_player_id=USER1_ID,
            players=[
                (USER2_ID, []),
                (USER1_ID, [("4", CLUBS), ("9", CLUBS), ("Q", CLUBS)]),
            ],
            played_combos=[],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("2", CLUBS)],
            turn=6,
        )
        game: Regicide = serializer.loads(dump)

        # player plays card with damage enough to defeat the enemy and won the game
        turn = {"cards": [("Q", CLUBS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert game.status == Status.WON
        assert 7 == game.turn
        assert game.active_player.id == USER1_ID
        assert 0 == len(game.enemy_deck)
        assert 3 == len(game.discard_deck)
        assert 1 == len(game.tavern_deck)
        assert 0 == len(game.played_combos)
        assert 0 == len(game.players[0].hand)
        assert 2 == len(game.players[1].hand)

    def test_play_cards__combo_from_twos(self, serializer: GameStateDataSerializer) -> None:
        """Tests playing card combo from 2x4"""
        dump = GameStateDto(
            enemy_deck=[("Q", HEARTS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=USER1_ID,
            players=[
                (USER2_ID, []),
                (USER1_ID, [("2", CLUBS), ("2", HEARTS), ("2", DIAMONDS), ("2", SPADES)]),
            ],
            played_combos=[[("10", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", CLUBS), ("4", CLUBS)],
            turn=6,
        )
        game = serializer.loads(dump)

        # player plays combo from 2x4, enemy has immune to hearts
        turn = {"cards": [("2", CLUBS), ("2", HEARTS), ("2", DIAMONDS), ("2", SPADES)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.PLAYING_CARDS == game.status
        assert 7 == game.turn
        assert game.active_player.id == USER2_ID
        assert 1 == len(game.enemy_deck)
        assert 1 == len(game.discard_deck)
        assert 0 == len(game.tavern_deck)
        assert 2 == len(game.played_combos)
        assert 1 == len(game.players[0].hand)
        assert 1 == len(game.players[1].hand)

    def test_play_cards__skip_playing_cards(self, serializer: GameStateDataSerializer) -> None:
        """Tests skipping playing card combo"""
        dump = GameStateDto(
            enemy_deck=[("Q", HEARTS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=USER1_ID,
            players=[
                (USER2_ID, []),
                (USER1_ID, [("10", HEARTS)]),
            ],
            played_combos=[[("10", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("3", CLUBS), ("4", CLUBS)],
            turn=6,
        )
        game = serializer.loads(dump)

        # empty cards means player skipped playing cards and want to discard if needed
        turn: dict = {"cards": []}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.DISCARDING_CARDS == game.status
        assert 7 == game.turn
        assert game.active_player.id == USER1_ID
        assert 1 == len(game.enemy_deck)
        assert 1 == len(game.discard_deck)
        assert 2 == len(game.tavern_deck)
        assert 1 == len(game.played_combos)
        assert 0 == len(game.players[0].hand)
        assert 1 == len(game.players[1].hand)

    def test_play_cards__combo_with_ace(self, serializer: GameStateDataSerializer) -> None:
        """Tests playing card combo from ace and card"""
        dump = GameStateDto(
            enemy_deck=[("Q", DIAMONDS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=USER1_ID,
            players=[
                (USER2_ID, [("3", CLUBS)]),
                (USER1_ID, [("5", CLUBS), ("10", SPADES), ("K", DIAMONDS), ("A", DIAMONDS)]),
            ],
            played_combos=[[("4", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[("4", CLUBS)],
            turn=6,
        )
        game = serializer.loads(dump)

        # player plays combo from ace and 5, game moves to discard cards state
        turn = {"cards": [("5", CLUBS), ("A", DIAMONDS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.DISCARDING_CARDS, game.status
        assert 7 == game.turn
        assert game.active_player.id == USER1_ID
        assert 1 == len(game.enemy_deck)
        assert 1 == len(game.discard_deck)
        assert 1 == len(game.tavern_deck)
        assert 2 == len(game.played_combos)
        assert 1 == len(game.players[0].hand)
        assert 2 == len(game.players[1].hand)

    def test_play_cards__combo_with_ace_and_hearts(
        self, serializer: GameStateDataSerializer
    ) -> None:
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
            active_player_id=USER1_ID,
            players=[
                (
                    USER1_ID,
                    [("4", HEARTS), ("10", HEARTS), ("J", HEARTS), ("Q", HEARTS), ("A", DIAMONDS)],
                ),
            ],
            played_combos=[[("4", SPADES)]],
            status=Status.PLAYING_CARDS.value,  # type: ignore
            tavern_deck=[],
            turn=6,
        )
        game = serializer.loads(dump)

        # player plays combo from ace and 4 (power - 5), game moves to discard cards state
        turn = {"cards": [("4", HEARTS), ("A", DIAMONDS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.DISCARDING_CARDS == game.status
        assert 7 == game.turn
        assert game.active_player.id == USER1_ID
        assert 1 == len(game.enemy_deck)
        assert 2 == len(game.discard_deck)
        assert 5 == len(game.tavern_deck)
        assert 2 == len(game.played_combos)
        assert 3 == len(game.players[0].hand)

    def test_play_cards__invalid_turn(self, serializer: GameStateDataSerializer) -> None:
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
            active_player_id=USER1_ID,
            players=[
                (
                    USER1_ID,
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
        game = serializer.loads(dump)

        with pytest.raises(InvalidTurnDataError):
            game.make_turn(game.active_player.id, None)  # type: ignore
        with pytest.raises(InvalidTurnDataError):
            game.make_turn(game.active_player.id, {})
        with pytest.raises(InvalidTurnDataError):
            game.make_turn(game.active_player.id, [(CLUBS, "5")])  # type: ignore

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
            with pytest.raises(exc):
                game.make_turn(game.active_player.id, {"cards": combo})

    def test_discard_cards(self, serializer: GameStateDataSerializer) -> None:
        """Tests discarding cards"""
        dump = GameStateDto(
            enemy_deck=[("Q", DIAMONDS)],
            discard_deck=[("4", CLUBS)],
            active_player_id=USER1_ID,
            players=[
                (USER2_ID, [("3", CLUBS)]),
                (USER1_ID, [("10", SPADES), ("K", DIAMONDS)]),
            ],
            played_combos=[[("4", SPADES)], [("5", CLUBS), ("A", DIAMONDS)]],
            status=Status.DISCARDING_CARDS.value,  # type: ignore
            tavern_deck=[("4", CLUBS)],
            turn=6,
        )
        game = serializer.loads(dump)
        turn = {"cards": [("K", DIAMONDS)]}
        game = game.make_turn(game.active_player.id, turn)

        assert Status.PLAYING_CARDS == game.status
        assert game.active_player.id == USER2_ID
        assert 2 == len(game.discard_deck)
        assert 2 == len(game.played_combos)
        assert 1 == len(game.tavern_deck)
        assert game.turn == dump.turn + 1
        assert 1 == len(game.players[0].hand)
        assert 1 == len(game.players[1].hand)
