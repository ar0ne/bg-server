"""Loaders"""
import logging
import os
from typing import Callable

from core.caches import CACHE, cached
from core.games.engine import GameEngine
from core.resources.errors import GameModuleNotFound
from core.resources.models import Room
from core.resources.utils import lazy_import

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log = logging.getLogger(__name__)


# all game engines have to implement this function
FACTORY_FUNC_NAME = "create_engine"


@cached(cache=CACHE, key_func=lambda n: n, ttl=3600)
def load_game_engine_builder(game_name: str) -> Callable | None:
    """
    Load game engine class.
    """
    path = f"{BASE_DIR}/core/games/{game_name}/engine.py"
    module = lazy_import("engine", path)
    factory_func = None
    try:
        factory_func = getattr(module, FACTORY_FUNC_NAME)
    except FileNotFoundError:
        log.error("Game module (%s) not found.", game_name)
    return factory_func


def get_engine(room: Room) -> GameEngine:
    """Get game engine instance"""
    name = room.game.name.lower()
    factory = load_game_engine_builder(name)
    if not factory:
        raise GameModuleNotFound
    return factory(room_id=room.id)
