"""Regicide main game file"""
import itertools
import random
from itertools import product
from typing import Iterable, List, Optional

from ..regicide.exceptions import (
    CardBelongsToAnotherError,
    InvalidGameStateError,
    InvalidPairComboError,
    MaxComboSizeExceededError,
    TurnOrderViolationError
)
from ..regicide.models import Card, CardCombo, Deck, Enemy, GameState, Player, Suit


def infinite_cycle(iters: Iterable):
    """Infinite loop generator"""
    while True:
        for it in iters:
            yield it


def cards_belong_to_player(player: Player, combo: CardCombo) -> bool:
    """True if all cards in combo from players hand"""
    return all(card in player.hand for card in combo)


def get_total_damage_to_enemy(enemy: Enemy, cards: List[CardCombo]) -> int:
    """Calculate attack from all played cards"""
    return sum(Card.get_attack_power(combo, enemy) for combo in cards)


def get_remaining_enemy_health(enemy: Enemy, combos: List[CardCombo]) -> int:
    """Calculate remaining enemy health"""
    return enemy.health - get_total_damage_to_enemy(enemy, combos)


def get_enemy_attack_damage(enemy: Enemy, combos: List[CardCombo]) -> int:
    """Get enemy's attack damage power"""
    return enemy.attack - enemy.get_reduced_attack_damage(combos)


def can_defeat_enemy_attack(player: Player, enemy: Enemy, played_combos: List[CardCombo]) -> bool:
    """True if player can defeat current enemy"""
    total_hand_damage = Card.get_combo_damage(player.hand)
    return total_hand_damage > get_enemy_attack_damage(enemy, played_combos)


def is_enemy_defeated(enemy: Enemy, cards: List[CardCombo]) -> bool:
    """True if enemy defeated (sum of attacks played cards is equal to enemy health or more)"""
    return enemy.health <= get_total_damage_to_enemy(enemy, cards)


def is_valid_duplicate_combo(rank: str, combo: CardCombo) -> bool:
    """True if it is valid combo from duplicated cards"""
    if not any(card.rank == rank for card in combo):
        return True
    if not all(card.rank == rank for card in combo):
        return False
    if Card.get_combo_damage(combo) > 10:
        return False
    return True


class Game:
    """Regicide game class"""

    DUPLICATED_COMBO_RANKS = (Card.TWO, Card.THREE, Card.FOUR, Card.FIVE)

    def __init__(self, players_ids: List[str]) -> None:
        """Init game"""
        assert len(players_ids), "No players found."
        # FIXME: OrderredDict?
        self.players = list(Player(p_id) for p_id in players_ids)
        # display number of current turn
        self.turn = 0
        # create empty decks
        self.discard_deck = Deck()
        self.tavern_deck = Deck()
        self.enemy_deck = Deck()

        # list of combos represents cards played against enemy before they went to discard pile
        self.played_combos: List[CardCombo] = []

        # randomly peek first player
        random.shuffle(self.players)
        self.next_player_loop = infinite_cycle(self.players)
        self.first_player = self.toggle_next_player_turn()
        # setup game state
        self.state = GameState.CREATED

    @property
    def is_playing_cards_state(self) -> bool:
        """True if game is in play cards state"""
        return self.state == GameState.PLAYING_CARDS

    @property
    def is_discarding_cards_state(self) -> bool:
        """True if game is discard cards state"""
        return self.state == GameState.DISCARDING_CARDS

    @property
    def current_enemy(self) -> Optional[Card]:
        """Gets current enemy"""
        return self.enemy_deck.peek()

    @staticmethod
    def start_new_game(players_ids: List[str]) -> "Game":
        """Create new game"""
        game = Game(players_ids)
        # create tavern and enemy decks
        game._create_tavern_deck()
        game._create_enemy_deck()
        # ensure we clear piles
        game.discard_deck.clear()
        game.played_combos = []
        # players draw X random cards on hands
        for player in game.players:
            player.hand = game.tavern_deck.pop_many(player.hand_size)
        # first player could play cards now
        game.state = GameState.PLAYING_CARDS
        game.turn = 1
        return game

    @staticmethod
    def play_cards(game: "Game", player: Player, combo: CardCombo) -> None:
        """Play cards"""
        game._assert_can_play_cards(player, combo)
        enemy = game.current_enemy
        # remove cards from player's hand
        player.remove_cards_from_hand(combo)
        # activate suits powers if possible
        game._process_played_combo(player, enemy, combo)
        # add cards to played cards deck
        game.played_combos.append(combo)
        # move to the next state
        game.state = GameState.DISCARDING_CARDS
        # check has been enemy defeated
        enemy_defeated = is_enemy_defeated(enemy, game.played_combos)
        if enemy_defeated:
            # no need to discard cards
            game.state = GameState.PLAYING_CARDS
            # pull next enemy from castle deck and discard defeated enemy and played cards
            game._pull_next_enemy()
            # transit to won state if enemy deck is empty now
            if not len(game.enemy_deck):
                game.state = GameState.WON
                return
        else:
            if get_enemy_attack_damage(enemy, game.played_combos) <= 0:
                # enemy can't attack, let next player to play cards
                game.state = GameState.PLAYING_CARDS
                game.toggle_next_player_turn()
            elif not can_defeat_enemy_attack(player, enemy, game.played_combos):
                # player must have cards on hand enough to deal with enemies attack, otherwise
                # game lost
                game.state = GameState.LOST
                return
        game.turn += 1

    @staticmethod
    def discard_cards(game: "Game", player: Player, combo: CardCombo) -> None:
        """Discard cards to defeat from enemy attack"""
        game._assert_can_discard_cards(player, combo)
        # remove cards from player's hand
        player.remove_cards_from_hand(combo)
        # move cards to discard pile
        game.discard_deck.append(combo)
        # next player could play card
        game.state = GameState.PLAYING_CARDS
        game.toggle_next_player_turn()
        game.turn += 1

    @staticmethod
    def get_game_state(game: "Game") -> dict:
        """Returns state of the game and all public information"""
        enemy = game.current_enemy
        # fmt: off
        return {
            "discard_deck_size": len(game.discard_deck),
            "played_combos": [
                [str(card) for card in combo]
                for combo in game.played_combos
            ],
            "enemy": {
                "card": str(enemy),
                "health": enemy.health,
                "health_left": get_remaining_enemy_health(enemy, game.played_combos),
                "attack": enemy.attack,
                "attack_left": get_enemy_attack_damage(enemy, game.played_combos),
            }
            if enemy else None,
            "first_player": str(game.first_player),
            "players": [str(p) for p in game.players],
            "state": str(game.state),
            "turn": game.turn,
            # players hands (perhaps depend on current user)
            "hand_size": game.first_player.hand_size,
            "hands": {
                str(player): [str(card) for card in player.hand]
                for player in game.players
            },
        }
        # fmt: on

    def toggle_next_player_turn(self) -> Player:
        """Change first player to next"""
        self.first_player = next(self.next_player_loop)
        return self.first_player

    def find_player(self, player_id: str) -> Optional[Player]:
        """Find player by id"""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

    def _assert_can_play_cards(self, player: Player, combo: CardCombo) -> None:
        """Assert player can play cards"""
        if not self.is_playing_cards_state:
            raise InvalidGameStateError
        if player not in self.players:
            raise Exception  # FIXME
        if not combo:
            raise Exception  # FIXME
        if player != self.first_player:
            raise TurnOrderViolationError
        if not cards_belong_to_player(player, combo):
            raise CardBelongsToAnotherError
        combo_size = len(combo)
        if combo_size == 1:
            return
        if any(card.rank == Card.ACE for card in combo):
            if combo_size > 2:
                raise MaxComboSizeExceededError
        else:
            if any(
                not is_valid_duplicate_combo(rank, combo) for rank in self.DUPLICATED_COMBO_RANKS
            ):
                raise InvalidPairComboError

    def _assert_can_discard_cards(self, player: Player, combo: CardCombo) -> None:
        """Assert can player discard these cards"""
        if not self.is_discarding_cards_state:
            raise InvalidGameStateError
        if player != self.first_player:
            raise TurnOrderViolationError
        if player not in self.players:
            raise Exception  # FIXME
        if not cards_belong_to_player(player, combo):
            raise CardBelongsToAnotherError
        if not combo:
            raise Exception  # FIXME
        enemy = self.current_enemy
        # damage from combo without suits power should be enough to deal with enemies attack damage
        combo_damage = Card.get_combo_damage(combo)
        if get_enemy_attack_damage(enemy, self.played_combos) > combo_damage:
            raise Exception  # FIXME

    def _pull_next_enemy(self) -> None:
        """Remove current enemy, throw off played cards to discard"""
        enemy = self.enemy_deck.pop()
        # if damage was equal to enemy health as a bonus we put card on top of tavern
        if not get_remaining_enemy_health(enemy, self.played_combos):
            self.tavern_deck.append(enemy)
        else:
            self.discard_deck.append(enemy)
        # move cards from played to discard pile
        flat_played_combos = list(itertools.chain.from_iterable(self.played_combos))
        self.discard_deck.append(flat_played_combos)
        # clean up played cards
        self.played_combos = []

    def _process_played_combo(self, player: Player, enemy: Enemy, combo: CardCombo) -> None:
        """Process played combo"""
        combo_damage = Card.get_attack_power(combo, enemy)
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
            players_loop = infinite_cycle(players)
            # add cards to players' hands
            list(map(lambda c: next(players_loop).hand.append(c), draw_cards))

    def _create_tavern_deck(self) -> None:
        """Create tavern cards deck"""
        ranks = (*map(str, range(2, 11)), Card.ACE)
        combinations = product(ranks, Suit.list_values())
        players_deck = list(map(lambda c: Card(suit=Suit(c[1]), rank=c[0]), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        enemy_ranks = (Card.JACK, Card.QUEEN, Card.KING)
        face_combs = product(enemy_ranks, Suit.list_values())
        enemy_deck = list(map(lambda c: Card(suit=Suit(c[1]), rank=c[0]), face_combs))
        jacks, queens, kings = enemy_deck[:4], enemy_deck[4:8], enemy_deck[8:]
        list(map(random.shuffle, (jacks, queens, kings)))
        self.enemy_deck = Deck([*jacks, *queens, *kings])
