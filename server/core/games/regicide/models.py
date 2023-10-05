"""Models"""
import enum
import json
import random
from typing import List, Optional, TypeVar, Union

Enemy = TypeVar("Enemy", bound="Card")
CardCombo = List["Card"]
CardHand = List["Card"]


class CardRank(enum.Enum):
    """Represents card rank"""

    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"


class GameState(enum.Enum):
    """Represents current state of the game"""

    CREATED = "created"
    PLAYING_CARDS = "playing_cards"
    DISCARDING_CARDS = "discarding_cards"
    LOST = "lost"
    WON = "won"


class Suit(enum.Enum):
    """Represents suit of the card"""

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

    def remove_cards_from_hand(self, combo: CardCombo) -> None:
        """Removes cards from hand"""
        self.hand = list(filter(lambda c: c not in combo, self.hand))

    def __str__(self) -> str:
        """To string"""
        return self.id


class Card:
    """Card"""

    ATTACK = {
        CardRank.TWO: 2,
        CardRank.THREE: 3,
        CardRank.FOUR: 4,
        CardRank.FIVE: 5,
        CardRank.SIX: 6,
        CardRank.SEVEN: 7,
        CardRank.EIGHT: 8,
        CardRank.NINE: 9,
        CardRank.TEN: 10,
        CardRank.JACK: 10,
        CardRank.QUEEN: 15,
        CardRank.KING: 20,
        CardRank.ACE: 1,
    }
    HEALTH = {
        CardRank.JACK: 20,
        CardRank.QUEEN: 30,
        CardRank.KING: 40,
    }

    def __init__(self, rank: Union[str, CardRank], suit: Union[Suit, str]) -> None:
        """Init Card"""
        self.rank = CardRank(rank) if isinstance(rank, str) else rank
        self.suit = Suit(suit) if isinstance(suit, str) else suit

    @property
    def health(self) -> int:
        """Get health"""
        return self.HEALTH[self.rank]

    @property
    def attack(self) -> int:
        """Get attack power"""
        return self.ATTACK[self.rank]

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
        """
        Calculate reduced enemy attack value if combo contains spades and enemy doesn't have
        immune
        """
        return (
            self.get_attack_power(combo, self)
            if self.suit != Suit.SPADES and any(card.suit == Suit.SPADES for card in combo)
            else 0
        )

    def get_reduced_attack_damage(self, combos: List[CardCombo]) -> int:
        """Calculate reduced enemy attack by played cards"""
        return sum(self.get_reduced_attack_power(combo) for combo in combos)

    def __str__(self) -> str:
        """To string"""
        return f"{self.suit.value} {self.rank}"

    def __eq__(self, other) -> bool:
        """True if object are equal"""
        if isinstance(other, Card):
            return (self.rank, self.suit.value) == (other.rank, other.suit.value)
        if isinstance(other, tuple) or isinstance(other, list):
            return (self.rank, self.suit.value) == (other[0], other[1])
        return NotImplemented


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
