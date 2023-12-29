"""Game utilities"""
from typing import List

from core.games.regicide.dto import FlatCard
from core.games.regicide.models import CardHand


def to_flat_hand(hand: CardHand) -> List[FlatCard]:
    """Flats card hand object"""
    # CardHand() => [("4", "♣"), (("5", "♣"))]
    return [(card.rank.value, card.suit.value) for card in hand]  # type: ignore
