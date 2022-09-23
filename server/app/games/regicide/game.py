"""Regicide main game file"""
import enum
import itertools
import json
import random
from dataclasses import dataclass, asdict
from itertools import product
from typing import List, Optional, Iterable, Union, TypeVar, Dict, Tuple

Enemy = TypeVar("Enemy", bound="Card")
PlayedCards = List[List["Card"]]
Combo = List["Card"]
Hand = List["Card"]


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

    def __init__(self, id: str, hand: Optional[Hand] = None, hand_size: int = 7) -> None:
        """Init player"""
        self.id = id
        self.hand: Hand = hand if hand else []
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
    def is_double_damage(combo: Combo, enemy: Enemy) -> bool:
        """True if possible to double cards attack"""
        return enemy.suit != Suit.CLUBS and any(card.suit == Suit.CLUBS for card in combo)

    @classmethod
    def get_attack_power(cls, combo: Combo, enemy: Enemy) -> int:
        """Calculate cards attack power"""
        damage = cls.get_combo_damage(combo)
        if cls.is_double_damage(combo, enemy):
            # if enemy doesn't have immune and played clubs we double attack power
            damage *= 2
        return damage

    @staticmethod
    def get_combo_damage(combo: Combo) -> int:
        """Calculate damage of combo"""
        return sum(card.attack for card in combo)

    def get_reduced_attack_power(self, combo: Combo) -> int:
        """Calculate reduced enemy attack value if combo contains spades and enemy doesn't immune"""
        return self.suit != Suit.SPADES and sum(
            card.attack for card in combo if card.suit == Suit.SPADES
        )

    def get_reduced_attack_damage(self, cards: PlayedCards) -> int:
        """Calculate reduced enemy attack by played cards"""
        return sum(map(lambda c: self.get_reduced_attack_power(c), cards))

    def __str__(self) -> str:
        """To string"""
        return f"{self.suit.value} {self.rank.value}"


class Deck:
    """Card deck"""

    def __init__(self, cards: Optional[List[Card]] = None) -> None:
        """Init deck"""
        if not cards:
            cards = []
        self.cards: List[Card] = cards

    def peek(self) -> Optional[Card]:
        """Peek first element from the deck"""
        return self.cards[0] if self.cards else None

    def pop(self) -> Card:
        """Pop first element from the deck"""
        card = self.cards[0]
        self.cards = self.cards[1:]
        return card

    def pop_many(self, count: int = 1) -> List[Card]:
        """Pop first element from the deck"""
        assert count <= len(self.cards), "Can't pop more deck contains."
        cards = self.cards[:count]
        self.cards = self.cards[count:]
        return cards

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

    def shuffle(self) -> None:
        """Randomize deck"""
        random.shuffle(self.cards)

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


@dataclass(frozen=True)
class GameData:
    """Represents internal game state data"""

    discard_deck: List[Tuple[str, str]]
    first_player_id: str
    players: List[Tuple[str, List[Tuple[str, str]]]]
    state: str
    tavern_deck: List[Tuple[str, str]]
    turn: int


class Game:
    """Regicide game class"""

    def __init__(self, players_ids: List[str]) -> None:
        """Init game"""
        assert len(players_ids), "No players found."
        self.players = list(Player(p_id) for p_id in players_ids)
        # display number of current turn
        self.turn = 0
        # create empty decks
        self.discard_deck = Deck()
        self.tavern_deck = Deck()
        self.enemy_deck = Deck()

        # list of lists represents cards combo played against enemy before they went to discard pile
        self.played_cards: PlayedCards = []

        self.next_player_loop = cycle(self.players)
        # FIXME: randomize it, otherwise first player from list always start
        self.first_player = self.toggle_next_player_turn()
        # setup game state
        self.state = GameState.CREATED

    def create_new_game(self) -> None:
        """Create new game"""
        self.turn = 1
        # create tavern and enemy decks
        self._create_tavern_deck()
        self._create_enemy_deck()
        self.played_cards = []

        # players draw X random cards on hands
        for player in self.players:
            player.hand = self.tavern_deck.pop_many(player.hand_size)
        # first player could play cards now
        self.state = GameState.PLAYING_CARDS

    def load(self, data: GameData) -> None:
        """Load data"""
        self.turn = data.turn
        self.state = GameState(data.state)
        # fmt: off
        self.players = [
            Player(player_id, [
                Card(Suit(card[1]), Rank(card[0]))
                for card in hand
            ])
            for player_id, hand in data.players
        ]

        self.discard_deck = Deck([
            Card(Suit(suit), Rank(rank))
            for rank, suit in data.discard_deck]
        )
        self.tavern_deck = Deck([
            Card(Suit(suit), Rank(rank))
            for rank, suit in data.tavern_deck]
        )
        # fmt: on

        # shift players' loop until first player from data
        self.next_player_loop = cycle(self.players)
        while self.toggle_next_player_turn().id != data.first_player_id:
            pass

    def dump(self) -> GameData:
        """Dump current game state"""

        def flat_card(card: Card) -> Tuple[str, str]:
            return card.rank.value, card.suit.value  # type: ignore

        def flat_deck(deck: Deck) -> List[Tuple[str, str]]:
            return [flat_card(card) for card in deck.cards]

        def flat_hand(player: Player) -> List[Tuple[str, str]]:
            return [flat_card(card) for card in player.hand]

        return GameData(
            discard_deck=flat_deck(self.discard_deck),
            first_player_id=self.first_player.id,
            players=[(pl.id, flat_hand(pl)) for pl in self.players],
            state=self.state.value,  # type: ignore
            tavern_deck=flat_deck(self.tavern_deck),
            turn=self.turn,
        )

    @property
    def playing_cards_state(self) -> bool:
        """True if game is in play cards state"""
        return self.state == GameState.PLAYING_CARDS

    @property
    def discarding_cards_state(self) -> bool:
        """True if game is discard cards state"""
        return self.state == GameState.DISCARDING_CARDS

    def toggle_next_player_turn(self) -> Player:
        """Change first player to next"""
        self.turn += 1
        if len(self.players) == 1:
            # no need to update first player if it's solo game
            return self.first_player
        self.first_player = next(self.next_player_loop)
        return self.first_player

    def assert_can_start_game(self) -> None:
        if self.state != GameState.CREATED:
            raise Exception  # FIXME

    @staticmethod
    def cards_belong_to_player(player: Player, combo: Combo) -> bool:
        return all(card in player.hand for card in combo)

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
        combo_damage = Card.get_combo_damage(combo)
        if self.get_enemy_attack_damage(enemy, self.played_cards) > combo_damage:
            raise Exception  # FIXME

    def _pull_next_enemy(self) -> None:
        """Remove current enemy, throw off played cards to discard pile"""
        enemy = self.enemy_deck.pop()
        # move cards from played to discard pile
        flat_played_cards = list(itertools.chain.from_iterable(self.played_cards))

        if not self.get_remaining_enemy_health(enemy, self.played_cards):
            self.tavern_deck.append(enemy)
        else:
            self.discard_deck.append(enemy)

        self.discard_deck.append(flat_played_cards)

        # clean up played cards
        self.played_cards = []

    @staticmethod
    def get_total_damage_to_enemy(enemy: Enemy, cards: PlayedCards) -> int:
        """Calculate attack from all played cards"""
        return sum(Card.get_attack_power(combo, enemy) for combo in cards)

    def is_defeated(self, enemy: Enemy, cards: PlayedCards) -> bool:
        """True if enemy defeated (sum of attacks played cards is equal to enemy health or more)"""
        return enemy.health <= self.get_total_damage_to_enemy(enemy, cards)

    @staticmethod
    def get_enemy_attack_damage(enemy: Enemy, cards: PlayedCards) -> int:
        """Get enemy's attack damage power"""
        return enemy.attack - enemy.get_reduced_attack_damage(cards)

    @staticmethod
    def get_remaining_enemy_health(enemy: Enemy, cards: PlayedCards) -> int:
        """Calculate remaining enemy health"""
        return enemy.health - enemy.get_total_damage(cards)

    def _process_played_combo(self, player: Player, enemy: Enemy, combo: Combo) -> None:
        """Process played combo"""
        combo_damage = Card.get_combo_damage(combo)
        # if hearts - shuffle and move cards from discard to tavern deck
        if enemy.suit != Suit.HEARTS and any(Suit.HEARTS == card.suit for card in combo):
            # shuffle deck
            self.discard_deck.shuffle()
            # ensure we don't try to move to many cards
            discard_length = len(self.discard_deck)
            draw_count = combo_damage if combo_damage < discard_length else discard_length
            draw_cards = self.discard_deck.pop_many(draw_count)
            # add cards to bottom of tavern deck
            self.tavern_deck.append(draw_cards)
        # if diamonds - draw cards to players hands
        if enemy.suit != Suit.DIAMONDS and any(Suit.DIAMONDS == card.suit for card in combo):
            hands_capacity = sum(pl.hand_size - len(pl.hand) for pl in self.players)
            tavern_length = len(self.tavern_deck)
            # ensure we don't draw cards more than available
            draw_count = min(hands_capacity, tavern_length, combo_damage)
            draw_cards = self.tavern_deck.pop_many(draw_count)
            player_index = self.players.index(player)
            # create new players list starting from current player
            players = self.players[player_index:] + self.players[:player_index]
            # make infinite loop
            players_loop = cycle(players)
            # add cards to players' hands
            list(map(lambda c: next(players_loop).hand.append(c), draw_cards))

    def play_cards(self, player: Player, combo: Combo):
        """Play cards"""
        self.assert_can_play_cards(player, combo)

        enemy = self.current_enemy
        # remove cards from player's hand
        player.hand = list(filter(lambda c: c not in combo, player.hand))
        # activate suits powers if possible
        self._process_played_combo(player, enemy, combo)
        # add cards to played cards deck
        self.played_cards.append(combo)
        # check has been enemy defeated
        enemy_defeated = self.is_defeated(enemy, self.played_cards)
        if enemy_defeated:
            # pull next enemy from castle deck and discard defeated enemy and played cards
            self._pull_next_enemy()
            # transit to won state if enemy deck is empty now
            if not len(self.enemy_deck):
                self.state = GameState.WON
        else:
            # if enemy still has attack power, transit game to discard card state
            self.state = GameState.DISCARDING_CARDS

            if self.get_enemy_attack_damage(enemy, self.played_cards) <= 0:
                # enemy can't attack, let next player to play cards
                self.state = GameState.PLAYING_CARDS
                self.toggle_next_player_turn()
            elif not self.can_defeat_enemies_attack(player, enemy):
                # player must have cards on hand enough to deal with enemies attack, otherwise
                # game lost
                self.state = GameState.LOST

    def can_defeat_enemies_attack(self, player: Player, enemy: Enemy) -> bool:
        """True if player can defeat current enemy"""
        hand = player.hand
        total_hand_damage = Card.get_combo_damage(hand)
        return total_hand_damage > self.get_enemy_attack_damage(enemy, self.played_cards)

    def discard_cards(self, player: Player, combo: Combo) -> None:
        """Discard cards to defeat from enemy attack"""
        self.assert_can_discard_cards(player, combo)
        # move cards to discard pile
        self.discard_deck.append(combo)
        # next player could play card
        self.state = GameState.PLAYING_CARDS
        self.toggle_next_player_turn()

    def get_game_state(self) -> dict:
        """Returns state of the game and all public information"""
        enemy = self.current_enemy
        return {
            "discard_deck_size": len(self.discard_deck),
            "played_cards": [[str(card) for card in combo] for combo in self.played_cards],
            "enemy": {
                "card": str(enemy),
                "health": enemy.health,
                "attack": enemy.attack,
            }
            if enemy
            else None,
            "first_player": str(self.first_player),
            "players": [str(p) for p in self.players],
            "state": str(self.state),
            "turn": self.turn,
            # players hands (perhaps depend on current user)
            # TODO: add hand size
            "hand_size": self.first_player.hand_size,
            "hands": {str(player): [str(card) for card in player.hand] for player in self.players},
        }

    @property
    def current_enemy(self) -> Optional[Card]:
        """Gets current enemy"""
        return self.enemy_deck.peek()

    def _create_tavern_deck(self) -> None:
        """Create tavern cards deck"""
        ranks = (*map(str, range(2, 11)), Card.ACE)
        combinations = product(ranks, Suit.list_values())
        players_deck = list(map(lambda c: Card(suit=Suit(c[1]), rank=Rank(c[0])), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        enemy_ranks = (Card.JACK, Card.QUEEN, Card.KING)
        face_combs = product(enemy_ranks, Suit.list_values())
        enemy_deck = list(map(lambda c: Card(suit=Suit(c[1]), rank=Rank(c[0])), face_combs))
        jacks, queens, kings = enemy_deck[:4], enemy_deck[4:8], enemy_deck[8:]
        list(map(random.shuffle, (jacks, queens, kings)))
        self.enemy_deck = Deck([*jacks, *queens, *kings])


if __name__ == "__main__":
    game = Game(["joe", "bob"])
    pl1, pl2 = game.players

    print("init game")
    print(game.get_game_state())
    print("create new game")
    game.create_new_game()
    print(game.get_game_state())
    print("play a card")
    game.play_cards(pl1, [pl1.hand[0]])
    print(game.get_game_state())

    print("dump")
    dump = game.dump()
    print("new game")
    game.create_new_game()
    print(game.get_game_state())
    print("load previous save")
    game.load(dump)
    print(game.get_game_state())


    # game.discard_cards(pl1, [pl1.hand[1]])
    # print(game.get_game_state())
    # game.play_cards(pl2, [pl2.hand[4]])
    # print(game.get_game_state())
