"""Regicide main game file"""
import itertools
import random
from itertools import product
from typing import Optional, List, Iterable

from server.app.games.regicide.models import Deck, GameState, Card, Suit, Player, CardCombo, Enemy


def cycle(iters: Iterable):
    """Infinite loop generator"""
    while True:
        for it in iters:
            yield it


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
        self.played_cards: List[CardCombo] = []

        # randomly peek first player
        random.shuffle(self.players)
        self.next_player_loop = cycle(self.players)
        self.first_player = self.toggle_next_player_turn()
        # setup game state
        self.state = GameState.CREATED

    def start_new_game(self) -> None:
        """Create new game"""
        self.turn = 1
        # create tavern and enemy decks
        self._create_tavern_deck()
        self._create_enemy_deck()
        # ensure we clear piles
        self.discard_deck.clear()
        self.played_cards = []

        # players draw X random cards on hands
        for player in self.players:
            player.hand = self.tavern_deck.pop_many(player.hand_size)
        # first player could play cards now
        self.state = GameState.PLAYING_CARDS

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
        self.first_player = next(self.next_player_loop)
        return self.first_player

    @staticmethod
    def cards_belong_to_player(player: Player, combo: CardCombo) -> bool:
        return all(card in player.hand for card in combo)

    def assert_can_play_cards(self, player: Player, combo: CardCombo) -> None:
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

    def assert_can_discard_cards(self, player: Player, combo: CardCombo) -> None:
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
    def get_total_damage_to_enemy(enemy: Enemy, cards: List[CardCombo]) -> int:
        """Calculate attack from all played cards"""
        return sum(Card.get_attack_power(combo, enemy) for combo in cards)

    def is_defeated(self, enemy: Enemy, cards: List[CardCombo]) -> bool:
        """True if enemy defeated (sum of attacks played cards is equal to enemy health or more)"""
        return enemy.health <= self.get_total_damage_to_enemy(enemy, cards)

    @staticmethod
    def get_enemy_attack_damage(enemy: Enemy, combos: List[CardCombo]) -> int:
        """Get enemy's attack damage power"""
        return enemy.attack - enemy.get_reduced_attack_damage(combos)

    def get_remaining_enemy_health(self, enemy: Enemy, combos: List[CardCombo]) -> int:
        """Calculate remaining enemy health"""
        return enemy.health - self.get_total_damage_to_enemy(enemy, combos)

    def _process_played_combo(self, player: Player, enemy: Enemy, combo: CardCombo) -> None:
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

    def play_cards(self, player: Player, combo: CardCombo):
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

    def discard_cards(self, player: Player, combo: CardCombo) -> None:
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
        # fmt: off
        return {
            "discard_deck_size": len(self.discard_deck),
            "played_cards": [
                [str(card) for card in combo]
                for combo in self.played_cards
            ],
            "enemy": {
                "card": str(enemy),
                "health": enemy.health,
                "health_left": self.get_remaining_enemy_health(enemy, self.played_cards),
                "attack": enemy.attack,
                "attack_left": self.get_enemy_attack_damage(enemy, self.played_cards),
            }
            if enemy else None,
            "first_player": str(self.first_player),
            "players": [str(p) for p in self.players],
            "state": str(self.state),
            "turn": self.turn,
            # players hands (perhaps depend on current user)
            "hand_size": self.first_player.hand_size,
            "hands": {
                str(player): [str(card) for card in player.hand]
                for player in self.players
            },
        }
        # fmt: on

    @property
    def current_enemy(self) -> Optional[Card]:
        """Gets current enemy"""
        return self.enemy_deck.peek()

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
