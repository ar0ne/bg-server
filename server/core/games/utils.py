"""Utilities"""

from typing import Any, Iterable, Iterator


def infinite_cycle(iters: Iterable) -> Iterator[Any]:
    """Infinite loop generator"""
    while True:
        for it in iters:
            yield it
