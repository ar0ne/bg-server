"""Regicide game adapter"""
from typing import List

from server.games.base import AbstractGame, Id
from server.games.regicide.dto import FlatCard, GameData
from server.games.regicide.game import Game
from server.games.regicide.models import Card
from server.games.regicide.utils import dump_data, load_data
from server.resources.models import GameTurn


class RegicideGameAdapter(AbstractGame):
    """Regicide game adapter"""

    def __init__(self, room_id: Id) -> None:
        """Init adapter"""
        self.room_id = room_id

    async def setup(self, players: List[Id]) -> None:
        """Setup new game"""
        game = Game.start_new_game(players)
        await self._save_game_state(game)

    async def update(self, player_id: Id, data: List[FlatCard]) -> None:
        """Update game state"""
        # transform from flat cards to Card objects
        data = list(map(lambda c: Card(c[0], c[1]), data))
        last_game_data = await self._get_latest_game_state()
        game = load_data(last_game_data)
        # player = game.find_player(player_id)
        player = game.first_player
        # if not player:
        #     raise Exception  # FIXME
        if game.is_playing_cards_state:
            Game.play_cards(game, player, data)
        elif game.is_discarding_cards_state:
            Game.discard_cards(game, player, data)
        else:
            # game ended?
            raise Exception  # FIXME
        # save changes
        await self._save_game_state(game)

    async def poll(self, player: Id) -> GameData:
        """Poll the last turn data"""
        last_turn_data = await self._get_latest_game_state()
        # data should be for specific player only
        return last_turn_data or {}

    async def _get_latest_game_state(self) -> GameData:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        return GameData(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        dump = dump_data(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=dump)
