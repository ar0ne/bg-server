"""Tic Tac Toe game engine"""

from core.games.base import AbstractGame

# FIXME: move duplicated code to BaseGame class


class GameEngine(AbstractGame):
    """Game engine"""

    def __init__(self, room_id: Id) -> None:
        """init engine"""
        self.room_id = room_id
        self.loader = None  # FIXME

    async def setup(self, players: List[Id]) -> None:
        """Setup game"""
        game = Game.start_new_game(players)
        await self._save_game_state(game)

    async def update(self, player_id: Id, turn: GameDataTurn) -> None:
        """Update game state"""
        if not self.is_valid_turn(turn):
            # FIXME: do something
            pass
        self._save_game_state(game)

    async def poll(self, player_id: Id | None = None) -> GameData | None:
        """Poll the last game state"""
        last_turn_state = await self._get_latest_game_state()
        if not last_turn_state:
            return None
        game = self.loader.load(last_turn_state)
        return asdict(serialize_game_data(game, player_id))

    async def _get_latest_game_state(self) -> GameStateDto | None:
        """Get the latest game state from db"""
        turn = await GameTurn.filter(room_id=self.room_id).order_by("-turn").first()
        if not turn:
            return None
        return GameStateDto(**turn.data)

    async def _save_game_state(self, game: Game) -> None:
        """persist game state into db"""
        dump = self.loader.upload(game)
        await GameTurn.create(room_id=self.room_id, turn=game.turn, data=dump)

    def is_valid_turn(self, turn: GameDataTurn) -> bool:
        """True if this is valid game turn"""
        # FIXME: should we game and check current state
        return True
