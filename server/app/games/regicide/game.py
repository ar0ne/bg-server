"""Regicide main game file"""
import json
import random
from dataclasses import dataclass
from itertools import product
from typing import List, Iterable, Tuple, Collection, Optional

HEARTS = "hearts"
SPADES = "spades"
CLUBS = "clubs"
DIAMONDS = "diamonds"
SUITS = (CLUBS, DIAMONDS, HEARTS, SPADES)

KING = "K"
QUEEN = "Q"
ACE = "A"
JACK = "J"


@dataclass
class Player:
    """Player"""


@dataclass
class Rank:
    value: str


@dataclass
class Card:
    """Card"""

    suit: str
    rank: Rank


@dataclass
class Hand:
    """Hand"""

    cards: List[Card]
    player: Player


class Deck:
    """Card deck"""

    def __init__(self, cards: Optional[Collection[Card]] = None) -> None:
        """Init deck"""
        if not cards:
            cards = []
        self.cards = cards

    def __str__(self) -> str:
        """To string"""
        return str(self.cards)

    def __len__(self) -> int:
        """Length of card deck"""
        return len(self.cards)


class Game:
    """Game class"""

    def __init__(self, players: Iterable[Player]) -> None:
        self.players = players
        self.tavern_deck = self._create_tavern_deck()
        self.enemy_deck = self._create_enemy_deck()
        self.discard_deck = Deck()
        self.is_running = False

    def _create_tavern_deck(self) -> Deck:
        ranks = (*map(str, range(2, 11)), ACE)
        combinations = product(ranks, SUITS)
        players_deck = list(map(lambda c: Card(suit=c[0], rank=Rank(c[1])), combinations))
        random.shuffle(players_deck)
        return Deck(players_deck)

    def _create_enemy_deck(self) -> Deck:
        """Create cards"""
        enemy_ranks = (JACK, QUEEN, KING)
        face_combs = product(enemy_ranks, SUITS)
        enemy_deck = list(map(lambda c: Card(suit=c[0], rank=Rank(c[1])), face_combs))
        jacks, queens, kings = enemy_deck[:4], enemy_deck[4:8], enemy_deck[8:]
        list(map(random.shuffle, (jacks, queens, kings)))
        return Deck([*jacks, *queens, *kings])


if __name__ == "__main__":
    pl = Player()
    game = Game([pl])
    print(len(game.tavern_deck))
    print(game.tavern_deck)

    print(len(game.enemy_deck))
    print(game.enemy_deck)
