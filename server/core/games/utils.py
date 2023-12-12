"""Utilities"""

from typing import Iterable


def infinite_cycle(iters: Iterable):
    """Infinite loop generator"""
    while True:
        for it in iters:
            yield it
