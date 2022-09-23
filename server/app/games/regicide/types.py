"""Types"""
from typing import TypeVar, List, Tuple

from server.app.games.regicide.models import Card

Enemy = TypeVar("Enemy", bound=Card)
CardCombo = List[Card]
CardHand = List[Card]
FlatCard = Tuple[str, str]
