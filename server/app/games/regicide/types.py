"""Types"""
from typing import TypeVar, List, Tuple

Enemy = TypeVar("Enemy", bound="Card")
PlayedCards = List[List["Card"]]
Combo = List["Card"]
Hand = List["Card"]
FlatCard = Tuple[str, str]
