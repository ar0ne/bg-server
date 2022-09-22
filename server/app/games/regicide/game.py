"""Regicide main game file"""
import enum
import random
from dataclasses import dataclass
from itertools import product
from typing import List, Optional, Iterable, Union


class Suits(enum.Enum):
    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"

    @classmethod
    def list(cls) -> List[str]:
        return list(map(lambda c: c.name, cls))


ACE = "A"
KING = "K"
QUEEN = "Q"
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


@dataclass(frozen=True)
class Card:
    """Card"""

    ATTACK = {
        ACE: 1,
        JACK: 10,
        QUEEN: 15,
        KING: 20,
    }
    HEALTH = {
        JACK: 20,
        QUEEN: 30,
        KING: 40,
    }

    suit: Suits
    rank: Rank

    @property
    def health(self) -> int:
        """Get health"""
        if self.suit in self.HEALTH:
            return self.HEALTH[self.suit]
        # can it be used for discarding
        return 0

    @property
    def attack(self) -> int:
        """Get attack power"""
        if self.suit in self.ATTACK:
            if self.suit == Suits.CLUBS:
                # TODO: what if enemy has immune ?
                return self.ATTACK[self.suit] * 2
            return self.ATTACK[self.suit]
        return int(self.rank.value)


class Deck:
    """Card deck"""

    def __init__(self, cards: Optional[List[Card]] = None) -> None:
        """Init deck"""
        if not cards:
            cards = []
        self.cards = cards

    def peek(self) -> Optional[Card]:
        """Peek first element from the deck"""
        return self.cards[0] if self.cards else None

    def pop(self) -> Card:
        """Pop first element from the deck"""
        card = self.cards[0]
        self.cards = self.cards[1:]
        return card

    def draw_cards(self, count: int = 1) -> List[Card]:
        """Draw cards and reveal them from deck"""
        # assert we can draw
        if len(self.cards) < count:
            raise Exception  # FIXME
        draw = self.cards[:count]
        self.cards = self.cards[count:]
        return draw

    def append(self, cards: Union[Card, List[Card]]) -> None:
        """Append single or several cards to the end of a deck"""
        if isinstance(cards, List):
            self.cards = self.cards + cards
        else:
            self.cards.append(cards)

    def clear(self) -> int:
        """Return size of cleaned deck"""
        size = len(self.cards)
        self.cards = []
        return size

    def __str__(self) -> str:
        """To string"""
        return str(self.cards)

    def __len__(self) -> int:
        """Length of card deck"""
        return len(self.cards)


def cycle(iters: Iterable):
    """Infinite loop generator"""
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
        # represents cards played against current enemy before they went to discard pile
        self.played_cards_deck = Deck()
        self.turn = 0

    def start_game(self) -> None:
        """Player draw cards"""
        self.assert_can_start_game()
        for player in self.players:
            self.players_hand[player.id] = self.tavern_deck.draw_cards(HAND_SIZE)
        self.state = GameState.running

    def _next_player_turn(self) -> Player:
        """Change first player to next"""
        if len(self.players) == 1:
            # no need to update first player if it's solo game
            return self.first_player
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
        if player != self.first_player:
            raise Exception  # FIXME
        for card in cards:
            if card not in self.players_hand[player.id]:
                raise Exception  # FIXME
        # TODO: check if it's combination of Ace and any card
        # TODO: check if it's 2+2+.., 3+3+.. combo

    def is_current_enemy_defeated(self) -> bool:
        """True if enemy defeated, True if sum of played cards is equal to enemy health"""
        cards = self.played_cards_deck.cards
        subtracted_health = 2  # FIXME: calculate all cards and their suits power
        enemy = self.get_current_enemy()
        if enemy.health <= subtracted_health:
            return True
        return False

    def _defeat_enemy(self) -> None:
        """Defeat current enemy"""
        enemy = self.enemy_deck.pop()
        # TODO: move to defeated enemies
        if not len(self.enemy_deck):
            # transit to won state if enemy deck is empty now
            self.state = GameState.won
        # remove all played cards from the deck
        self.played_cards_deck.clear()

    def play_cards(self, player: Player, cards: Union[Card, List[Card]]):
        """Play cards"""
        if isinstance(cards, Card):
            cards = [cards]
        self.assert_can_play_cards(player, cards)

        self.turn += 1
        # reveal cards from player's hand
        self.players_hand[player.id] = list(
            filter(lambda c: c not in cards, self.players_hand[player.id])
        )
        # add cards to played cards deck
        self.played_cards_deck.append(cards)
        # check has been enemy defeated
        if self.is_current_enemy_defeated():
            self._defeat_enemy()

        self._next_player_turn()

    def get_game_state(self) -> dict:
        """Returns state of the game and all public information"""
        enemy = self.get_current_enemy()
        return {
            "discard_deck_size": len(self.discard_deck),
            "played_deck": str(self.played_cards_deck),
            "enemy": {
                "health": enemy.health,
                "attack": enemy.attack,
            },
            "first_player": self.first_player,
            "players": self.players,
            "state": self.state,
            "turn": self.turn,
            # players hands (perhaps depend on current user)
            # TODO: add hand size
            "hands": {
                player: str(self.players_hand[player.id])
                for player in self.players
                if player.id in self.players_hand
            },
        }

    def get_current_enemy(self) -> Optional[Card]:
        """Gets current enemy"""
        return self.enemy_deck.peek()

    def _create_tavern_deck(self) -> None:
        """Create tavern cards deck"""
        ranks = (*map(str, range(2, 11)), ACE)
        combinations = product(ranks, Suits.list())
        players_deck = list(map(lambda c: Card(suit=c[0], rank=Rank(c[1])), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        enemy_ranks = (JACK, QUEEN, KING)
        face_combs = product(enemy_ranks, Suits.list())
        enemy_deck = list(map(lambda c: Card(suit=c[0], rank=Rank(c[1])), face_combs))
        jacks, queens, kings = enemy_deck[:4], enemy_deck[4:8], enemy_deck[8:]
        list(map(random.shuffle, (jacks, queens, kings)))
        self.enemy_deck = Deck([*jacks, *queens, *kings])


if __name__ == "__main__":
    pl1 = Player("Joe")
    pl2 = Player("Bob")
    game = Game([pl1, pl2])

    print(game.get_game_state())
    game.start_game()
    print(game.get_game_state())
    game.play_cards(pl1, [game.players_hand[pl1.id][0]])
    print(game.get_game_state())
    game.play_cards(pl2, [game.players_hand[pl2.id][4]])
    print(game.get_game_state())
