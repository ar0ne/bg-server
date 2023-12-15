"""Loaders"""
import logging
import os

from core.caches import CACHE, cached
from core.games.base import AbstractGame
from core.resources.models import Game
from core.resources.utils import lazy_import

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log = logging.getLogger(__name__)


@cached(cache=CACHE, key_func=lambda n: n, ttl=3600)
def load_game_module(game_name: str):
    """
    Load game engine class.
    """
    path = f"{BASE_DIR}/core/games/{game_name}/engine.py"
    module = lazy_import("engine", path)
    try:
        return getattr(module, "GameEngine")
    except FileNotFoundError:
        log.error("Game module (%s) not found.", game_name)


def get_engine(game: Game, *args, **kwargs) -> AbstractGame:
    """Get game engine instance"""
    name = game.name.lower()
    module = load_game_module(name)
    if not module:
        raise Exception  # FIXME
    if not hasattr(module, "create_engine"):
        raise Exception  # FIXME
    return module.create_engine(*args, **kwargs)
