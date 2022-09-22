"""Regicide main game file"""
import enum
import itertools
import json
import random
from dataclasses import dataclass
from itertools import product
from typing import List, Optional, Iterable, Union, TypeVar


Enemy = TypeVar("Enemy", bound="Card")
PlayedCards = List[List["Card"]]
Combo = List["Card"]


class Suits(enum.Enum):
    CLUBS = "♣"
    DIAMONDS = "♦"
    HEARTS = "♥"
    SPADES = "♠"

    @classmethod
    def list_values(cls) -> List[str]:
        """Generates list of suits values"""
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

    @staticmethod
    def is_double_damage(combo: Combo, enemy: Enemy) -> bool:
        """True if possible to double cards attack"""
        return enemy.suit != Suits.CLUBS and any(card.suit == Suits.CLUBS for card in combo)

    @classmethod
    def get_attack_power(cls, combo: Combo, enemy: Enemy) -> int:
        """Calculate cards attack power"""
        damage = sum(map(lambda c: c.attack, combo))
        if cls.is_double_damage(combo, enemy):
            # if enemy doesn't have immune and played clubs we double attack power
            damage *= 2
        return damage

    def get_reduced_attack_power(self, combo: Combo) -> int:
        """Calculate reduced enemy attack value if combo contains spades and enemy doesn't immune"""
        return self.suit != Suits.SPADES and sum(
            card.attack for card in combo if card.suit == Suits.SPADES
        )

    def get_reduced_attack_damage(self, cards: PlayedCards) -> int:
        """Calculate reduced enemy attack by played cards"""
        return sum(map(lambda c: self.get_reduced_attack_power(c), cards))

    def get_damage(self, cards: PlayedCards) -> int:
        """Calculate attack from all played cards"""
        return sum(map(lambda c: Card.get_attack_power(c, self), cards))

    def is_defeated(self, cards: PlayedCards) -> bool:
        """True if enemy defeated (sum of attacks played cards is equal to enemy health or more)"""
        return self.health <= self.get_damage(cards)

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

    def cards_belong_to_player(self, player: Player, combo: Combo) -> bool:
        return all(card in self.players_hand[player.id] for card in combo)

    def assert_can_play_cards(self, player: Player, combo: Combo) -> None:
        """Assert player can play cards"""
        if not self.playing_cards_state:
            raise Exception  # FIXME
        if player not in self.players:
            raise Exception  # FIXME
        if not combo:
            raise Exception  # FIXME
        if player != self.first_player:
            raise Exception  # FIXME
        if not self.cards_belong_to_player(player, combo):
            raise Exception  # FIXME

        # TODO: check if it's combination of Ace and any card
        # TODO: check if it's 2+2+.., 3+3+.. combo

    def assert_can_discard_cards(self, player: Player, combo: Combo) -> None:
        """Assert can player discard these cards"""
        if not self.discarding_cards_state:
            raise Exception  # FIXME
        if not self.cards_belong_to_player(player, combo):
            raise Exception  # FIXME
        if player != self.first_player:
            raise Exception  # FIXME
        if player not in self.players:
            raise Exception  # FIXME
        if not combo:
            raise Exception  # FIXME
        enemy = self.current_enemy
        # damage from combo without suits power should be enough to deal with enemies attack damage
        combo_damage = sum(card.attack for card in combo)
        if enemy.attack - enemy.get_reduced_attack_damage(self.played_cards) > combo_damage:
            raise Exception  # FIXME

        # TODO: check if it's combination of Ace and any card
        # TODO: check if it's 2+2+.., 3+3+.. combo

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

    def play_cards(self, player: Player, cards: Combo):
        """Play cards"""
        self.assert_can_play_cards(player, cards)

        enemy = self.current_enemy
        # remove cards from player's hand
        self.players_hand[player.id] = list(
            filter(lambda c: c not in cards, self.players_hand[player.id])
        )
        # add cards to played cards deck
        self.played_cards.append(cards)
        # check has been enemy defeated
        if enemy.is_defeated(self.played_cards):
            self.defeat_enemy()

        if not len(self.enemy_deck):
            # transit to won state if enemy deck is empty now
            self.state = GameState.WON
        if not self.can_defeat_enemies_attack(player, enemy):
            # if player doesn't have cards on hand enough to deal with enemies attack - game lost
            self.state = GameState.LOST

        if enemy.attack - enemy.get_reduced_attack_damage(self.played_cards) > 0:
            # if player should deal with enemy attack transit to discard card state then
            self.state = GameState.DISCARDING_CARDS
        else:
            # otherwise, it's next player turn
            self.toggle_next_player_turn()

    def can_defeat_enemies_attack(self, player: Player, enemy: Enemy) -> bool:
        """True if player can defeat current enemy"""
        # TODO:
        return True

    def discard_cards(self, player: Player, cards: Combo) -> None:
        """Discard cards to defeat from enemy attack"""
        self.assert_can_discard_cards(player, cards)

        # TODO: if player can't defeat game lost ?

        # increase turn counter
        self.turn += 1

    def get_game_state(self) -> dict:
        """Returns state of the game and all public information"""
        enemy = self.current_enemy
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

    @property
    def current_enemy(self) -> Optional[Card]:
        """Gets current enemy"""
        return self.enemy_deck.peek()

    def _create_tavern_deck(self) -> None:
        """Create tavern cards deck"""
        ranks = (*map(str, range(2, 11)), ACE)
        combinations = product(ranks, Suits.list_values())
        players_deck = list(map(lambda c: Card(suit=Suits(c[1]), rank=Rank(c[0])), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        enemy_ranks = (JACK, QUEEN, KING)
        face_combs = product(enemy_ranks, Suits.list_values())
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
    game.discard_cards(pl1, [game.players_hand[pl1.id][1]])
    print(game.get_game_state())
    game.play_cards(pl2, [game.players_hand[pl2.id][4]])
    print(game.get_game_state())
