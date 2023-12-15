"""Game data serializer"""
from abc import ABC, abstractmethod

from core.games.base import GameData, GameDataTurn, Id
from core.games.regicide.dto import GameStateDto, GameTurnDataDto
from core.games.regicide.game import Game, infinite_cycle
from core.games.regicide.models import Card, CardHand, Deck, Player, Status, Suit
from core.games.regicide.utils import to_flat_hand
from core.games.transform import GameStateDataSerializer, GameTurnDataSerializer


class RegicideGameTurnDataSerializer(GameTurnDataSerializer):
    """Regicide game data serilizer"""

    @staticmethod
    def dump(game: Game, **kwargs) -> GameTurnDataDto:  # type: ignore[override]
        """Serialize game object to game turn DTO for a player"""
        player_id: str | None = kwargs.get("player_id")
        player = None
        if player_id:
            player = game.find_player(player_id)
        top_enemy = game.enemy_deck.peek()
        return GameTurnDataDto(
            enemy_deck_size=len(game.enemy_deck),
            discard_size=len(game.discard_deck),
            enemy=(top_enemy.rank.value, top_enemy.suit.value),
            first_player_id=game.first_player.id,
            player_id=player_id or "",
            played_combos=[to_flat_hand(combo) for combo in game.played_combos],
            status=game.status.value,  # type: ignore
            tavern_size=len(game.tavern_deck),
            turn=game.turn,
            hand=to_flat_hand(player.hand) if player else None,
        )


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
        game.first_player = game.find_player(data.first_player_id)
        # fmt: on

        # shift players' loop until first player from data
        game.next_player_loop = infinite_cycle(game.players)
        while game.toggle_next_player_turn().id != data.first_player_id:
            pass

        game.turn = data.turn
        game.status = Status(data.status)
        return game

    @staticmethod
    def dump(game: Game, **kwargs) -> GameStateDto:
        """Serialize game object into game state DTO"""

        return GameStateDto(
            enemy_deck=to_flat_hand(game.enemy_deck.cards),
            discard_deck=to_flat_hand(game.discard_deck.cards),
            first_player_id=game.first_player.id,
            players=[(pl.id, to_flat_hand(pl.hand)) for pl in game.players],
            played_combos=[to_flat_hand(combo) for combo in game.played_combos],
            status=game.status.value,  # type: ignore
            tavern_deck=to_flat_hand(game.tavern_deck.cards),
            turn=game.turn,
        )
