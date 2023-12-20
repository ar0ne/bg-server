"""Custom types"""
import uuid
from typing import Any, Dict, Union

Id = Union[str, uuid.UUID]

GameData = Dict[str, Any]
GameDataTurn = Dict[str, Any]
GameState = Dict[str, Any]
Game = Any  # FIXME
