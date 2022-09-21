"""Regicide main game file"""
import enum
import random
from dataclasses import dataclass
from itertools import product
from typing import List, Optional, Iterable

HEARTS = "hearts"
SPADES = "spades"
CLUBS = "clubs"
DIAMONDS = "diamonds"
SUITS = (CLUBS, DIAMONDS, HEARTS, SPADES)

KING = "K"
QUEEN = "Q"
ACE = "A"
JACK = "J"

# FIXME: should be dynamic
HAND_SIZE = 7


@dataclass(frozen=True)
class Player:
    """Player"""

    id: str

    def __str__(self):
        return self.id


@dataclass(frozen=True)
class Rank:
    value: str

    def __str__(self) -> str:
        """to string"""
        if self.value == CLUBS:
            return CLUBS
        if self.value == HEARTS:
            return HEARTS
        if self.value == SPADES:
            return SPADES
        return DIAMONDS


@dataclass
class Card:
    """Card"""

    suit: str
    rank: Rank


class Deck:
    """Card deck"""

    def __init__(self, cards: Optional[List[Card]] = None) -> None:
        """Init deck"""
        if not cards:
            cards = []
        self.cards = cards

    def peek(self) -> Optional[Card]:
        return self.cards[0] if self.cards else None

    def draw_cards(self, count: int = 1) -> List[Card]:
        """Draw cards and reveal them from deck"""
        # assert we can draw
        if len(self.cards) < count:
            raise Exception  # FIXME
        draw = self.cards[:count]
        self.cards = self.cards[count:]
        return draw

    def __str__(self) -> str:
        """To string"""
        return str(self.cards)

    def __len__(self) -> int:
        """Length of card deck"""
        return len(self.cards)


def cycle(iters: Iterable):
    while True:
        for it in iters:
            yield it


class GameState(enum.Enum):
    created = "created"
    running = "running"
    lost = "lost"
    won = "won"


class Game:
    """Regicide game class"""

    def __init__(self, players: List[Player]) -> None:
        """Init game"""
        assert len(players), "No players found."
        self.players = players
        self._create_tavern_deck()
        self._create_enemy_deck()
        self.discard_deck = Deck()
        # self.defeated_enemies = Deck()
        self.next_player_loop = cycle(self.players)
        self.first_player = self._next_player_turn()
        self.state = GameState.created
        self.players_hand = {}

    def start_game(self) -> None:
        """Player draw cards"""
        self.assert_can_start_game()
        for player in self.players:
            self.players_hand[player.id] = self.tavern_deck.draw_cards(HAND_SIZE)
        self.state = GameState.running

    def _next_player_turn(self) -> Player:
        """Change first player to next"""
        next_player = next(self.next_player_loop)
        self.first_player = next_player
        return next_player

    def assert_can_start_game(self) -> None:
        if self.state != GameState.created:
            raise Exception  # FIXME

    def assert_can_play_cards(self, player: Player, cards: List[Card]) -> None:
        """Assert player can play cards"""
        if self.state != GameState.running:
            raise Exception  # FIXME
        if player not in self.players:
            raise Exception  # FIXME
        if not cards:
            raise Exception  # FIXME
        for card in cards:
            if card not in self.players_hand[player]:
                raise Exception  # FIXME

    def play_cards(self, player: Player, cards: List[Card]):
        """Play cards"""
        self.assert_can_play_cards(player, cards)

    def get_game_state(self) -> dict:
        """Returns state of the game and all public information"""
        return {
            "discard_deck_size": len(self.discard_deck),
            "enemy": self.enemy_deck.peek(),
            "first_player": self.first_player,
            "players": self.players,
            "state": self.state,
            # players hands (perhaps depend on current user)
            "hands": {
                player: self.players_hand[player.id]
                for player in self.players
                if player.id in self.players_hand
            },
        }

    def _create_tavern_deck(self) -> None:
        """Create tavern cards deck"""
        ranks = (*map(str, range(2, 11)), ACE)
        combinations = product(ranks, SUITS)
        players_deck = list(map(lambda c: Card(suit=c[0], rank=Rank(c[1])), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        enemy_ranks = (JACK, QUEEN, KING)
        face_combs = product(enemy_ranks, SUITS)
        enemy_deck = list(map(lambda c: Card(suit=c[0], rank=Rank(c[1])), face_combs))
        jacks, queens, kings = enemy_deck[:4], enemy_deck[4:8], enemy_deck[8:]
        list(map(random.shuffle, (jacks, queens, kings)))
        self.enemy_deck = Deck([*jacks, *queens, *kings])


if __name__ == "__main__":
    pl = Player("123")
    pl2 = Player("jee")
    game = Game([pl, pl2])

    print(game.get_game_state())
    game.start_game()
    print(game.get_game_state())

