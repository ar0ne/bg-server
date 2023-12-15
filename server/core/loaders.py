"""Loaders"""
import os

from core.games.base import AbstractGame
from core.resources.models import Game
from core.resources.utils import lazy_import

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# FIXME: cache it
def get_engine(game: Game) -> AbstractGame:
    """Get game engine class"""
    game_name = game.name.lower()
    module = lazy_import("engine", f"{BASE_DIR}/core/games/{game_name}/engine.py")
    return getattr(module, "GameEngine")
