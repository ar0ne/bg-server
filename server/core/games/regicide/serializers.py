"""Game data serializer"""
from core.games.regicide.dto import GameStateDto, GameTurnDataDto, PlayerHand
from core.games.regicide.game import (
    Regicide,
    get_enemy_attack_damage,
    get_remaining_enemy_health,
    infinite_cycle,
)
from core.games.regicide.models import Card, Deck, Player, Status, Suit
from core.games.regicide.utils import to_flat_hand
from core.types import GameState


class RegicideGameTurnDataSerializer:
    """Regicide game data serilizer"""

    @staticmethod
    def dumps(game: Regicide, **kwargs) -> GameState:  # type: ignore[override]
        """Serialize game object to game turn DTO for a player"""
        player_id: str | None = kwargs.get("player_id")
        player = None
        if player_id:
            player = game.find_player(player_id)
        top_enemy = game.enemy_deck.peek()
        hands = [
            PlayerHand(
                id=pl.id,
                size=len(pl.hand),  # use actual size
                hand=to_flat_hand(pl.hand) if player and player_id == pl.id else None,
            )
            for pl in game.players
        ]
        enemy_state = (
            get_remaining_enemy_health(top_enemy, game.played_combos) if top_enemy else None,
            get_enemy_attack_damage(top_enemy, game.played_combos) if top_enemy else None,
        )
        return GameTurnDataDto(
            enemy_deck_size=max(len(game.enemy_deck) - 1, 0),
            discard_size=len(game.discard_deck),
            enemy=(top_enemy.rank.value, top_enemy.suit.value) if top_enemy else None,
            enemy_state=enemy_state,
            active_player_id=game.active_player.id,
            player_id=str(player.id) if player else "",
            played_combos=[to_flat_hand(combo) for combo in game.played_combos],
            status=game.status.value,  # type: ignore
            tavern_size=len(game.tavern_deck),
            turn=game.turn,
            hands=hands,
        ).asdict()


class RegicideGameStateDataSerializer:
    """Regicide game state serializer"""

    @staticmethod
    def loads(data: GameStateDto, **kwargs) -> Regicide:
        """Deserialize game state DTO to game object"""
        # fmt: off
        game = Regicide(list(map(lambda p: p[0], data.players)))
        game.players = [
            Player(player_id, [
                Card(card[0], Suit(card[1]))
                for card in hand
            ])
            for player_id, hand in data.players
        ]
        game.played_combos = [
            [
                Card(card[0], Suit(card[1]))
                for card in combo
            ]
            for combo in data.played_combos
        ]
        game.discard_deck = Deck([
            Card(rank, Suit(suit))
            for rank, suit in data.discard_deck
        ])
        game.tavern_deck = Deck([
            Card(rank, Suit(suit))
            for rank, suit in data.tavern_deck
        ])
        game.enemy_deck = Deck([
            Card(rank, Suit(suit))
            for rank, suit in data.enemy_deck
        ])
        # FIXME: raise exception if player not found?
        game.active_player = game.find_player(data.active_player_id)  # type: ignore
        # fmt: on

        # shift players' loop until first player from data
        game.next_player_loop = infinite_cycle(game.players)
        while game.toggle_next_player_turn().id != data.active_player_id:
            pass

        game.turn = data.turn
        game.status = Status(data.status)
        return game

    @staticmethod
    def dumps(game: Regicide, **kwargs) -> GameState:
        """Serialize game object into game state DTO"""

        return GameStateDto(
            enemy_deck=to_flat_hand(game.enemy_deck.cards),
            discard_deck=to_flat_hand(game.discard_deck.cards),
            active_player_id=game.active_player.id,
            players=[(pl.id, to_flat_hand(pl.hand)) for pl in game.players],
            played_combos=[to_flat_hand(combo) for combo in game.played_combos],
            status=game.status.value,  # type: ignore
            tavern_deck=to_flat_hand(game.tavern_deck.cards),
            turn=game.turn,
        ).asdict()
