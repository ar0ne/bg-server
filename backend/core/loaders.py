"""Loaders"""
import logging
import os

from typing import Callable

from core.games.engine import GameEngine
from core.resources.errors import GameModuleNotFound
from core.resources.models import Room
from core.resources.utils import load_module

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

log = logging.getLogger(__name__)


# all game engines have to implement this function
FACTORY_FUNC_NAME = "create_engine"


def load_game_engine_factory(game_name: str) -> Callable | None:
    """
    Load game engine factory function.
    """
    # lazily load module of the game and cache it in sys.modules
    module = load_module(f"core.games.{game_name}.engine")
    if not module:
        return None
    try:
        return getattr(module, FACTORY_FUNC_NAME)
    except AttributeError:
        log.error("Can't load game engine builder (%s)", game_name)
    return None


async def get_engine(room: Room) -> GameEngine:
    """Get game engine instance"""
    name = room.game.name.lower()
    factory = load_game_engine_factory(name)
    if not factory:
        raise GameModuleNotFound
    return factory(room_id=room.id)
