"""Tests for converter"""
import pytest

from core.games.regicide.dto import GameStateDto
from core.games.regicide.game import Regicide as Game
from core.games.regicide.models import Card, CardRank, Deck, Player, Status, Suit
from core.games.regicide.serializers import RegicideGameStateDataSerializer
from core.games.serializers import GameStateDataSerializer


@pytest.fixture
def serializer():
    return RegicideGameStateDataSerializer()


class TestRegicideGameStateDataSerializers:
    """unit tests for game state data serializers"""

    def test_dumps_game_state(self, serializer: GameStateDataSerializer) -> None:
        """Tests dumping (upload) game state"""

        user_id = "user_id"
        game = Game([user_id])
        card = Card(suit=Suit.HEARTS, rank=CardRank.FOUR)
        game.active_player = Player(user_id, [card])
        game.players = [game.active_player]
        game.enemy_deck = Deck([Card(suit=Suit.SPADES, rank=CardRank.JACK)])
        game.tavern_deck = Deck([Card(suit=Suit.CLUBS, rank=CardRank.TWO)])
        game.played_combos = [
            [Card(suit=Suit.CLUBS, rank=CardRank.FIVE), Card(suit=Suit.HEARTS, rank=CardRank.ACE)],
            [Card(suit=Suit.SPADES, rank=CardRank.THREE)],
        ]
        game.discard_deck = Deck([Card(suit=Suit.DIAMONDS, rank=CardRank.NINE)])
        game.status = Status.DISCARDING_CARDS
        game.turn = 5

        dump = serializer.dumps(game)

        assert [("J", "♠")] == dump["enemy_deck"]
        assert [("2", "♣")] == dump["tavern_deck"]
        assert user_id == dump["active_player_id"]
        assert [(user_id, [("4", "♥")])] == dump["players"]
        assert [[("5", "♣"), ("A", "♥")], [("3", "♠")]] == dump["played_combos"]
        assert [("9", "♦")] == dump["discard_deck"]
        assert 5 == dump["turn"]
        assert Status.DISCARDING_CARDS.value == dump["status"]

    def test_load_data(self, serializer) -> None:
        """Tests loading game data"""
        user1_id = "user1_id"
        user2_id = "user2_id"
        dump = GameStateDto(
            enemy_deck=[("J", "♠")],
            discard_deck=[("9", "♦")],
            active_player_id=user2_id,
            players=[
                (user1_id, [("4", "♥")]),
                (user2_id, [("2", "♥")]),
            ],
            played_combos=[[("5", "♣"), ("A", "♥")], [("3", "♠")]],
            status="discarding_cards",  # type: ignore
            tavern_deck=[("2", "♣")],
            turn=20,
        )
        game = serializer.loads(dump)

        assert 20 == game.turn
        assert Status.DISCARDING_CARDS == game.status
        assert user2_id == game.active_player.id
        assert 1 == len(game.tavern_deck)
        assert CardRank.TWO == game.tavern_deck.cards[0].rank
        assert Suit.CLUBS == game.tavern_deck.cards[0].suit
        assert 2 == len(game.players)
        assert 1 == len(game.enemy_deck)
        assert CardRank.JACK == game.enemy_deck.cards[0].rank
        assert Suit.SPADES == game.enemy_deck.cards[0].suit
        assert 1 == len(game.discard_deck)
        assert CardRank.NINE == game.discard_deck.cards[0].rank
        assert Suit.DIAMONDS == game.discard_deck.cards[0].suit
        assert 2 == len(game.played_combos)
        assert Suit.CLUBS == game.played_combos[0][0].suit
        assert CardRank.FIVE == game.played_combos[0][0].rank
        assert Suit.HEARTS == game.played_combos[0][1].suit
        assert CardRank.ACE == game.played_combos[0][1].rank
        assert Suit.SPADES == game.played_combos[1][0].suit
        assert CardRank.THREE == game.played_combos[1][0].rank

        # TODO: check players' hands
