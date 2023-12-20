"""Loaders"""
import logging
import os
from typing import Callable

from core.caches import CACHE, cached
from core.games.base import GameEngine
from core.resources.models import Room
from core.resources.utils import lazy_import

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log = logging.getLogger(__name__)


@cached(cache=CACHE, key_func=lambda n: n, ttl=3600)
def load_game_engine_builder(game_name: str) -> Callable:
    """
    Load game engine class.
    """
    path = f"{BASE_DIR}/core/games/{game_name}/engine.py"
    module = lazy_import("engine", path)
    try:
        return getattr(module, "create_engine")
    except FileNotFoundError:
        log.error("Game module (%s) not found.", game_name)


def get_engine(room: Room) -> GameEngine:
    """Get game engine instance"""
    name = room.game.name.lower()
    builder = load_game_engine_builder(name)
    if not builder:
        raise Exception  # FIXME
    return builder(room_id=room.id)
