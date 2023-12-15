"""Loaders"""
import os

from core.caches import CACHE, cached
from core.games.base import AbstractGame
from core.resources.models import Game
from core.resources.utils import lazy_import

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


@cached(cache=CACHE, key_func=lambda g: g.name.lower(), ttl=3600)
def get_engine(game: Game) -> AbstractGame:
    """Get game engine class"""
    game_name = game.name.lower()
    module = lazy_import("engine", f"{BASE_DIR}/core/games/{game_name}/engine.py")
    return getattr(module, "GameEngine")
