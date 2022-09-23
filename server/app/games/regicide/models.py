"""Models"""
import enum
import json
import random
from dataclasses import dataclass
from typing import List, Optional, Union

from server.app.games.regicide.types import CardHand, CardCombo, Enemy


class GameState(enum.Enum):
    CREATED = "created"
    PLAYING_CARDS = "playing_cards"
    DISCARDING_CARDS = "discarding_cards"
    LOST = "lost"
    WON = "won"


class Suit(enum.Enum):
    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"

    @classmethod
    def list_values(cls) -> List[str]:
        """Generates list of suits values"""
        return list(map(lambda c: c.value, cls))


class Player:
    """Player"""

    def __init__(self, id: str, hand: Optional[CardHand] = None, hand_size: int = 7) -> None:
        """Init player"""
        self.id = id
        self.hand: CardHand = hand if hand else []
        self.hand_size = hand_size

    def __str__(self) -> str:
        """To string"""
        return self.id


@dataclass(frozen=True)
class Rank:
    """Card rank"""

    value: str


class Card:
    """Card"""

    ACE = "A"
    KING = "K"
    QUEEN = "Q"
    JACK = "J"

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

    def __init__(self, suit: Suit, rank: Rank) -> None:
        """Init Card"""
        self.suit = suit
        self.rank = rank

    @property
    def health(self) -> int:
        """Get health"""
        return self.HEALTH[self.rank.value]

    @property
    def attack(self) -> int:
        """Get attack power"""
        return self.ATTACK[self.rank.value]

    @staticmethod
    def is_double_damage(combo: CardCombo, enemy: Enemy) -> bool:
        """True if possible to double cards attack"""
        return enemy.suit != Suit.CLUBS and any(card.suit == Suit.CLUBS for card in combo)

    @classmethod
    def get_attack_power(cls, combo: CardCombo, enemy: Enemy) -> int:
        """Calculate cards attack power"""
        damage = cls.get_combo_damage(combo)
        if cls.is_double_damage(combo, enemy):
            # if enemy doesn't have immune and played clubs we double attack power
            damage *= 2
        return damage

    @staticmethod
    def get_combo_damage(combo: CardCombo) -> int:
        """Calculate damage of combo"""
        return sum(card.attack for card in combo)

    def get_reduced_attack_power(self, combo: CardCombo) -> int:
        """Calculate reduced enemy attack value if combo contains spades and enemy doesn't immune"""
        return self.suit != Suit.SPADES and sum(
            card.attack for card in combo if card.suit == Suit.SPADES
        )

    def get_reduced_attack_damage(self, combos: List[CardCombo]) -> int:
        """Calculate reduced enemy attack by played cards"""
        return sum(self.get_reduced_attack_power(combo) for combo in combos)

    def __str__(self) -> str:
        """To string"""
        return f"{self.suit.value} {self.rank.value}"


class Deck:
    """Card deck"""

    def __init__(self, cards: Optional[CardHand] = None) -> None:
        """Init deck"""
        if not cards:
            cards = []
        self.cards: CardHand = cards

    def peek(self) -> Optional[Card]:
        """Peek first element from the deck"""
        return self.cards[0] if self.cards else None

    def pop(self) -> Card:
        """Pop first element from the deck"""
        card = self.cards[0]
        self.cards = self.cards[1:]
        return card

    def pop_many(self, count: int = 1) -> CardCombo:
        """Pop first element from the deck"""
        assert count <= len(self.cards), "Can't pop more deck contains."
        cards = self.cards[:count]
        self.cards = self.cards[count:]
        return cards

    def append(self, cards: Union[Card, CardCombo]) -> None:
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

    def shuffle(self) -> None:
        """Randomize deck"""
        random.shuffle(self.cards)

    def __str__(self) -> str:
        """To string"""
        return json.dumps(self.cards)

    def __len__(self) -> int:
        """Length of card deck"""
        return len(self.cards)

