"""Game data serializer"""
from abc import ABC, abstractmethod

from core.games.base import GameData, GameDataSerializer, GameDataTurn, Id
from core.games.regicide.dto import GameTurnDataDto
from core.games.regicide.game import Game
from core.games.regicide.utils import to_flat_hand


class RegicideGameDataSerializer(GameDataSerializer):
    """Regicide game data serilizer"""

    @classmethod
    def serialize(cls, game: Game, player_id: str | None = None) -> GameTurnDataDto:
        """Serialize public game turn data for player"""
        player = None
        if player_id:
            player = game.find_player(player_id)
        top_enemy = game.enemy_deck.peek()
        return GameTurnDataDto(
            enemy_deck_size=len(game.enemy_deck),
            discard_size=len(game.discard_deck),
            enemy=(top_enemy.rank.value, top_enemy.suit.value),
            first_player_id=game.first_player.id,
            player_id=player_id,
            played_combos=[to_flat_hand(combo) for combo in game.played_combos],
            state=game.state.value,  # type: ignore
            tavern_size=len(game.tavern_deck),
            turn=game.turn,
            hand=to_flat_hand(player.hand) if player else None,
        )
