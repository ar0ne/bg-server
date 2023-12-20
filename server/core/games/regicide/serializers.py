"""Game data serializer"""
from abc import ABC, abstractmethod

from core.games.base import GameData, GameDataTurn, GameState
from core.games.regicide.dto import GameStateDto, GameTurnDataDto, PlayerHand
from core.games.regicide.game import (
    Game,
    get_enemy_attack_damage,
    get_remaining_enemy_health,
    infinite_cycle,
)
from core.games.regicide.models import Card, CardHand, Deck, Player, Status, Suit
from core.games.regicide.utils import to_flat_hand
from core.games.transform import GameStateDataSerializer, GameTurnDataSerializer
from core.types import Id


class RegicideGameTurnDataSerializer(GameTurnDataSerializer):
    """Regicide game data serilizer"""

    @staticmethod
    def dump(game: Game, **kwargs) -> GameDataTurn:  # type: ignore[override]
        """Serialize game object to game turn DTO for a player"""
        player_id: Id | None = kwargs.get("player_id")
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


class RegicideGameStateDataSerializer(GameStateDataSerializer):
    """Regicide game state serializer"""

    @staticmethod
    def load(data: GameStateDto, **kwargs) -> Game:  # type: ignore[override]
        """Deserialize game state DTO to game object"""
        # fmt: off
        game = Game(list(map(lambda p: p[0], data.players)))
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
        game.active_player = game.find_player(data.active_player_id)
        # fmt: on

        # shift players' loop until first player from data
        game.next_player_loop = infinite_cycle(game.players)
        while game.toggle_next_player_turn().id != data.active_player_id:
            pass

        game.turn = data.turn
        game.status = Status(data.status)
        return game

    @staticmethod
    def dump(game: Game, **kwargs) -> GameState:
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
