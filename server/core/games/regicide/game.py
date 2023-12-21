"""Regicide main game file"""
import itertools
import random
from itertools import product
from typing import Any, Iterable, List, Optional

from core.games.game import Game
from core.types import GameDataTurn

from ..exceptions import InvalidGameStateError, TurnOrderViolationError
from ..regicide.exceptions import (
    CardDoesNotBelongsToPlayerError,
    InvalidCardDataError,
    InvalidPairComboError,
    InvalidTurnDataError,
    MaxComboSizeExceededError,
    NotEnoughPowerToDiscard,
)
from ..regicide.models import Card, CardCombo, CardRank, Deck, Enemy, Player, Status, Suit
from ..utils import infinite_cycle

DUPLICATED_COMBO_RANKS = (CardRank.TWO, CardRank.THREE, CardRank.FOUR, CardRank.FIVE)
ENEMY_RANKS = (CardRank.JACK, CardRank.QUEEN, CardRank.KING)


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
    return max(0, enemy.attack - enemy.get_reduced_attack_damage(combos))


def can_defeat_enemy_attack(player: Player, enemy: Enemy, played_combos: List[CardCombo]) -> bool:
    """True if player can defeat current enemy"""
    total_hand_damage = Card.get_combo_damage(player.hand)
    return total_hand_damage >= get_enemy_attack_damage(enemy, played_combos)


def is_enemy_defeated(enemy: Enemy, cards: List[CardCombo]) -> bool:
    """True if enemy defeated (sum of attacks played cards is equal to enemy health or more)"""
    return enemy.health <= get_total_damage_to_enemy(enemy, cards)


def has_diamonds(combo: CardCombo) -> bool:
    """True if combo has diamond suit"""
    return any(Suit.DIAMONDS == card.suit for card in combo)


def has_hearts(combo: CardCombo) -> bool:
    """True if combo has hearts suit"""
    return any(Suit.HEARTS == card.suit for card in combo)


class Regicide(Game):
    """Regicide game class"""

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
        # setup game state
        self.status = Status.CREATED
        self.next_player_loop = infinite_cycle(self.players)
        self.active_player = None

    @property
    def is_playing_cards_state(self) -> bool:
        """True if game is in play cards state"""
        return self.status == Status.PLAYING_CARDS

    @property
    def is_discarding_cards_state(self) -> bool:
        """True if game is discard cards state"""
        return self.status == Status.DISCARDING_CARDS

    @property
    def is_game_in_progress(self) -> bool:
        """True if game is in progress"""
        return self.status in (Status.PLAYING_CARDS, Status.DISCARDING_CARDS)

    @property
    def current_enemy(self) -> Optional[Card]:
        """Gets current enemy"""
        return self.enemy_deck.peek()

    @classmethod
    def init_new_game(cls, players_ids: List[str]) -> "Regicide":
        """Create new game"""
        game = cls(players_ids)
        # create tavern and enemy decks
        game._create_tavern_deck()
        game._create_enemy_deck()
        # ensure we clear piles
        game.discard_deck.clear()
        game.played_combos = []
        # randomly peek first player
        random.shuffle(game.players)
        game.active_player = game.toggle_next_player_turn()
        # players draw X random cards on hands
        for player in game.players:
            hand = game.tavern_deck.pop_many(player.max_hand_size)
            player.hand = hand
        # first player could play cards now
        game.status = Status.PLAYING_CARDS
        game.turn = 1
        return game

    @staticmethod
    def make_turn(game: "Regicide", player_id: str, turn: GameDataTurn) -> "Regicide":
        """Player could make a turn"""
        validate_game_turn(game, player_id, turn)
        player = game.find_player(player_id)
        cards = list(map(lambda c: Card(c[0], c[1]), turn["cards"]))
        if game.is_playing_cards_state:
            game._play_cards(player, cards)
        elif game.is_discarding_cards_state:
            game._discard_cards(player, cards)
        game.turn += 1
        return game

    def _play_cards(self, player: Player, combo: CardCombo) -> None:
        """Play cards"""
        enemy = self.current_enemy
        # remove cards from player's hand
        player.remove_cards_from_hand(combo)
        # activate suits powers if possible
        self._process_played_combo(player, enemy, combo)
        # combo could be empty if player decided to skip
        if combo:
            # add cards to played cards deck
            self.played_combos.append(combo)
        # move to the next state
        self.status = Status.DISCARDING_CARDS
        # check has been enemy defeated
        if is_enemy_defeated(enemy, self.played_combos):
            # no need to discard cards
            self.status = Status.PLAYING_CARDS
            # pull next enemy from castle deck and discard defeated enemy and played cards
            self._pull_next_enemy()
            # transit to won state if enemy deck is empty now
            if not len(self.enemy_deck):
                self.status = Status.WON
        else:
            if get_enemy_attack_damage(enemy, self.played_combos) <= 0:
                # enemy can't attack, let next player to play cards
                self.status = Status.PLAYING_CARDS
                self.toggle_next_player_turn()
            elif not can_defeat_enemy_attack(player, enemy, self.played_combos):
                # player must have cards on hand enough to deal with enemies attack, otherwise
                # game lost
                self.status = Status.LOST

    def _discard_cards(self, player: Player, combo: CardCombo) -> None:
        """Discard cards to defeat from enemy attack"""
        # remove cards from player's hand
        player.remove_cards_from_hand(combo)
        # move cards to discard pile
        self.discard_deck.append(combo)
        # next player could play card
        self.status = Status.PLAYING_CARDS
        self.toggle_next_player_turn()

    def toggle_next_player_turn(self) -> Player:
        """Change active player to next"""
        self.active_player = next(self.next_player_loop)
        return self.active_player

    def find_player(self, player_id: str) -> Optional[Player]:
        """Find player by id"""
        for player in self.players:
            if player.id == player_id:
                return player
        return None

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
        if not combo:
            # user could skip playing cards and defeat enemy attack
            return
        combo_damage = Card.get_attack_power(combo, enemy)
        # if hearts - shuffle and move cards from discard to tavern deck
        if enemy.suit != Suit.HEARTS and has_hearts(combo):
            # shuffle deck
            self.discard_deck.shuffle()
            # ensure we don't try to move too many cards
            discard_length = len(self.discard_deck)
            draw_count = combo_damage if combo_damage < discard_length else discard_length
            draw_cards = self.discard_deck.pop_many(draw_count)
            # add cards to bottom of tavern deck
            self.tavern_deck.append(draw_cards)
        # if diamonds - draw cards to players hands
        if enemy.suit != Suit.DIAMONDS and has_diamonds(combo):
            hands_capacity = sum(pl.max_hand_size - len(pl.hand) for pl in self.players)
            tavern_length = len(self.tavern_deck)
            # ensure we don't draw cards more than available
            draw_count = min(hands_capacity, tavern_length, combo_damage)
            draw_cards = self.tavern_deck.pop_many(draw_count)
            player_index = self.players.index(player)
            # create new players list starting from current player
            players = self.players[player_index:] + self.players[:player_index]
            # filter only players with available spots
            players = list(filter(lambda p: len(p.hand) < p.max_hand_size, players))
            # make infinite loop
            players_loop = infinite_cycle(players)
            # add cards to players' hands
            for card in draw_cards:
                # filter only players with still available spots
                for player in players_loop:
                    if len(player.hand) >= player.max_hand_size:
                        continue
                    player.hand.append(card)
                    break

    def _create_tavern_deck(self) -> None:
        """Create tavern cards deck"""
        ranks = (*map(str, range(2, 11)), CardRank.ACE)
        combinations = product(ranks, Suit.values())
        players_deck = list(map(lambda c: Card(suit=Suit(c[1]), rank=c[0]), combinations))
        random.shuffle(players_deck)
        self.tavern_deck = Deck(players_deck)

    def _create_enemy_deck(self) -> None:
        """Create enemy cards deck"""
        face_combs = product(ENEMY_RANKS, Suit.values())
        enemy_deck = list(map(lambda c: Card(suit=Suit(c[1]), rank=c[0]), face_combs))
        jacks, queens, kings = enemy_deck[:4], enemy_deck[4:8], enemy_deck[8:]
        list(map(random.shuffle, (jacks, queens, kings)))
        self.enemy_deck = Deck([*jacks, *queens, *kings])


def validate_can_play_cards(game: Regicide, player: Player, combo: CardCombo) -> None:
    """Assert player can play cards"""
    if not cards_belong_to_player(player, combo):
        raise CardDoesNotBelongsToPlayerError
    combo_size = len(combo)
    if combo_size == 1:
        return
    if any(card.rank == CardRank.ACE for card in combo):
        if combo_size > 2:
            raise MaxComboSizeExceededError
    else:
        if len(set(map(lambda c: c.rank, combo))) != 1:
            raise InvalidPairComboError
        if combo[0].rank not in DUPLICATED_COMBO_RANKS:
            raise InvalidPairComboError
        if Card.get_combo_damage(combo) > 10:
            raise InvalidPairComboError


def validate_can_discard_cards(game: Regicide, player: Player, combo: CardCombo) -> None:
    """Assert can player discard these cards"""
    if not cards_belong_to_player(player, combo):
        raise CardDoesNotBelongsToPlayerError
    enemy = game.current_enemy
    # damage from combo without suits power should be enough to deal with enemies attack damage
    combo_damage = Card.get_combo_damage(combo)
    if get_enemy_attack_damage(enemy, game.played_combos) > combo_damage:
        raise NotEnoughPowerToDiscard


def is_valid_card(card: Any) -> bool:
    """True if card is valid"""
    try:
        Card(card[0], card[1])
    except ValueError:
        return False
    return True


def validate_game_turn(game: Regicide, player_id: str, turn: dict) -> None:
    """Verify it's a valid turn"""
    if not game.is_game_in_progress:
        raise InvalidGameStateError
    if not (turn and isinstance(turn, dict)):
        raise InvalidTurnDataError
    player = game.active_player
    if player.id != player_id:
        raise TurnOrderViolationError

    cards = turn.get("cards")
    if not cards and game.is_playing_cards_state:
        # user could skip turn and immediately move to discard state
        return
    if not all(is_valid_card(card) for card in cards):
        raise InvalidCardDataError

    combo = list(map(lambda c: Card(c[0], c[1]), cards))
    if game.is_playing_cards_state:
        validate_can_play_cards(game, player, combo)
    elif game.is_discarding_cards_state:
        validate_can_discard_cards(game, player, combo)
