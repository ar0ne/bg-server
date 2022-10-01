"""Game utilities"""
from typing import List

from server.games.regicide.dto import GameData, FlatCard
from server.games.regicide.game import Game, infinite_cycle
from server.games.regicide.models import GameState, Player, Card, Suit, Deck, CardHand


def load_data(game: Game, data: GameData) -> None:
    """Load data"""
    # fmt: off
    game.players = [
        Player(player_id, [
            Card(Suit(card[1]), card[0])
            for card in hand
        ])
        for player_id, hand in data.players
    ]
    game.played_combos = [
        [
            Card(Suit(card[1]), card[0])
            for card in combo
        ]
        for combo in data.played_combos
    ]
    game.discard_deck = Deck([
        Card(Suit(suit), rank)
        for rank, suit in data.discard_deck
    ])
    game.tavern_deck = Deck([
        Card(Suit(suit), rank)
        for rank, suit in data.tavern_deck
    ])
    game.enemy_deck = Deck([
        Card(Suit(suit), rank)
        for rank, suit in data.enemy_deck
    ])
    # fmt: on

    # shift players' loop until first player from data
    game.next_player_loop = infinite_cycle(game.players)
    while game.toggle_next_player_turn().id != data.first_player_id:
        pass

    game.turn = data.turn
    game.state = GameState(data.state)


def dump_data(game: Game) -> GameData:
    """Dump current game state"""

    def to_flat_hand(hand: CardHand) -> List[FlatCard]:
        """Flats card hand object"""
        return [(card.rank, card.suit.value) for card in hand]  # type: ignore

    # FIXME: on UI we don't need whole Taverna and Discard decks, only sizes

    return GameData(
        enemy_deck=to_flat_hand(game.enemy_deck.cards),
        discard_deck=to_flat_hand(game.discard_deck.cards),
        first_player_id=game.first_player.id,
        players=[(pl.id, to_flat_hand(pl.hand)) for pl in game.players],
        played_combos=[to_flat_hand(combo) for combo in game.played_combos],
        state=game.state.value,  # type: ignore
        tavern_deck=to_flat_hand(game.tavern_deck.cards),
        turn=game.turn,
    )
