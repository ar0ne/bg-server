"""Regicide main game file"""
import enum
import itertools
import json
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
        return list(map(lambda c: c.value, cls))


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


@dataclass(frozen=True)
class Rank:
    """Card rank"""

    value: str


@dataclass(frozen=True)
class Card:
    """Card"""

    ATTACK = {
        JACK: 10,
        QUEEN: 15,
        KING: 20,
        ACE: 1,
    }
    ATTACK.update({str(v): v for v in range(2, 11)})
    HEALTH = {
        JACK: 20,
        QUEEN: 30,
        KING: 40,
    }
    # HEALTH.update({str(v): v for v in range(2, 11)})

    suit: Suits
    rank: Rank

    @property
    def health(self) -> int:
        """Get health"""
        if self.rank.value in self.HEALTH:
            return self.HEALTH[self.rank.value]
        # TODO: can it be used for discarding? if not simplify
        return 0

    @property
    def attack(self) -> int:
        """Get attack power"""
        return self.ATTACK[self.rank.value]

    def __str__(self) -> str:
        """To string"""
        return f"{self.suit.value} {self.rank.value}"


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
        return json.dumps(self.cards)

    def __len__(self) -> int:
        """Length of card deck"""
        return len(self.cards)


def cycle(iters: Iterable):
    """Infinite loop generator"""
    while True:
        for it in iters:
            yield it


class GameState(enum.Enum):
    CREATED = "created"
    PLAYING_CARDS = "playing_cards"
    DISCARDING_CARDS = "discarding_cards"
    LOST = "lost"
    WON = "won"


class Game:
    """Regicide game class"""

    def __init__(self, players: List[Player]) -> None:
        """Init game"""
        assert len(players), "No players found."
        self.players = players
        self._create_tavern_deck()
        self._create_enemy_deck()
        #
        self.discard_deck = Deck()
        # self.defeated_enemies = Deck()
        self.next_player_loop = cycle(self.players)
        # FIXME: randomize it, otherwise first player from list always start
        self.first_player = self.toggle_next_player_turn()
        # setup game state
        self.state = GameState.CREATED
        # dict of lists of cards for each player
        self.players_hand = {}
        # list of lists represents cards combo played against enemy before they went to discard pile
        self.played_cards = []
        # list of all defeated enemies
        self.defeated_enemies = []
        # display number of current turn
        self.turn = 1

    @property
    def playing_cards_state(self) -> bool:
        """True if game is in play cards state"""
        return self.state == GameState.PLAYING_CARDS

    @property
    def discarding_cards_state(self) -> bool:
        """True if game is discard cards state"""
        return self.state == GameState.DISCARDING_CARDS

    def start_game(self) -> None:
        """Player draw cards"""
        self.assert_can_start_game()
        # players draw X random cards on hands
        for player in self.players:
            self.players_hand[player.id] = self.tavern_deck.draw_cards(HAND_SIZE)
        # first player could play cards now
        self.state = GameState.PLAYING_CARDS

    def toggle_next_player_turn(self) -> Player:
        """Change first player to next"""
        if len(self.players) == 1:
            # no need to update first player if it's solo game
            return self.first_player
        self.first_player = next(self.next_player_loop)
        return self.first_player

    def assert_can_start_game(self) -> None:
        if self.state != GameState.CREATED:
            raise Exception  # FIXME

    def cards_belong_to_player(self, player: Player, cards: List[Card]) -> bool:
        return all(card in self.players_hand[player.id] for card in cards)

    def assert_can_play_cards(self, player: Player, cards: List[Card]) -> None:
        """Assert player can play cards"""
        if not self.playing_cards_state:
            raise Exception  # FIXME
        if player not in self.players:
            raise Exception  # FIXME
        if not cards:
            raise Exception  # FIXME
        if player != self.first_player:
            raise Exception  # FIXME
        if not self.cards_belong_to_player(player, cards):
            raise Exception  # FIXME
        # TODO: check if it's combination of Ace and any card
        # TODO: check if it's 2+2+.., 3+3+.. combo

    def assert_can_discard_cards(self, player: Player, cards: List[Card]) -> None:
        """Assert can player discard these cards"""
        if not self.discarding_cards_state:
            raise Exception  # FIXME
        if not self.cards_belong_to_player(player, cards):
            raise Exception  # FIXME

    @staticmethod
    def doubling(enemy: Card, cards: List[Card]) -> bool:
        """True if possible to double cards attack"""
        return enemy.suit != Suits.CLUBS and any(card.suit == Suits.CLUBS for card in cards)

    def cards_power(self, enemy: Card, cards: List[Card]) -> int:
        """Calculate cards attack power"""
        attack_sum = sum(map(lambda c: c.attack, cards))
        if self.doubling(enemy, cards):
            # if enemy doesn't have immune and played clubs we double attack power
            attack_sum *= 2
        return attack_sum

    def is_current_enemy_defeated(self) -> bool:
        """True if enemy defeated (sum of attacks played cards is equal to enemy health or more)"""
        enemy = self.get_current_enemy()
        subtracted_health = sum(map(lambda c: self.cards_power(enemy, c), self.played_cards))
        if enemy.health <= subtracted_health:
            return True
        return False

    def defeat_enemy(self) -> None:
        """Defeat current enemy"""
        enemy = self.enemy_deck.pop()
        # move enemy to defeated list
        self.defeated_enemies.append(enemy)
        # move cards from played to discard pile
        flat_played_cards = list(itertools.chain.from_iterable(self.played_cards))
        self.discard_deck.append(flat_played_cards)
        # clean up played cards
        self.played_cards = []

    def play_cards(self, player: Player, cards: Union[Card, List[Card]]):
        """Play cards"""
        if isinstance(cards, Card):
            cards = [cards]
        self.assert_can_play_cards(player, cards)
        # remove cards from player's hand
        self.players_hand[player.id] = list(
            filter(lambda c: c not in cards, self.players_hand[player.id])
        )
        # add cards to played cards deck
        self.played_cards.append(cards)
        # check has been enemy defeated
        if self.is_current_enemy_defeated():
            self.defeat_enemy()
            # transit to won state if enemy deck is empty now
            if not len(self.enemy_deck):
                self.state = GameState.WON
        self.toggle_next_player_turn()

    def discard_cards(self, player: Player, cards: Union[Card, List[Card]]) -> None:
        """Discard cards to defeat from enemy attack"""
        self.assert_can_discard_cards(player, cards)

        # TODO: if player can't defeat game lost

        # increase turn counter
        self.turn += 1

    def get_game_state(self) -> dict:
        """Returns state of the game and all public information"""
        enemy = self.get_current_enemy()
        return {
            "discard_deck_size": len(self.discard_deck),
            "played_cards": str(self.played_cards),
            "enemy": {
                "card": str(enemy),
                "health": enemy.health,
                "attack": enemy.attack,
            },
            "first_player": self.first_player,
            "players": str(self.players),
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
        players_deck = list(map(lambda c: Card(suit=Suits(c[1]), rank=Rank(c[0])), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        enemy_ranks = (JACK, QUEEN, KING)
        face_combs = product(enemy_ranks, Suits.list())
        enemy_deck = list(map(lambda c: Card(suit=Suits(c[1]), rank=Rank(c[0])), face_combs))
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
