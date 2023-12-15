"""
Caches
"""
import functools
import logging
import time
from time import monotonic
from typing import Any, Callable, Optional, Protocol, TypeVar, cast

from tornado import gen
from tornado.concurrent import Future

FuncType = Callable[..., Any]
F = TypeVar("F", bound=FuncType)  # pylint: disable=invalid-name


class Cache(Protocol):
    """Cache protocol"""

    def get(self, key):
        ...

    def set(self, key, value, expires=0):
        ...

    def add(self, key, value, expires=0):
        ...

    def incr(self, key):
        ...


class SimpleCache:
    """Simple cache. Just stores things in a dict of fixed size."""

    def __init__(self, limit: int = 10) -> None:
        self._cache = {}
        self._cache_order = []
        self.limit = limit

    def get(self, key: str) -> Any:
        return self._get(key)

    def _get(self, key: str):
        value, deadline = self._cache.get(key, (None, None))
        if deadline and deadline < monotonic():
            self._cache.pop(key)
            self._cache_order.remove(key)
        else:
            return value

    def set(self, key: str, value: Any, expires: int = 0) -> None:
        if key in self._cache and self._cache_order[-1] != key:
            idx = self._cache_order.index(key)
            del self._cache_order[idx]
            self._cache_order.append(key)
        else:
            if len(self._cache) >= self.limit:
                oldest = self._cache_order.pop(0)
                self._cache.pop(oldest)
            self._cache_order.append(key)

        if not expires:
            deadline = None
        else:
            deadline = monotonic() + expires

        self._cache[key] = (value, deadline)

    def add(self, key: str, value: Any, expires: int = 0) -> bool:
        if self._get(key) is not None:
            return False
        self.set(key, value, expires)
        return True

    def incr(self, key: str) -> Any | None:
        if self._get(key) is not None:
            value, deadline = self._cache[key]
            value = value + 1
            self._cache[key] = (value, deadline)
        else:
            value = None
        return value


class DummyAsyncCache:
    """Dummy Async Cache. Just stores things in a dict of fixed size."""

    def __init__(self, limit=10):
        self._cache = {}
        self._cache_order = []
        self.limit = limit

    def get(self, key: str):
        f = Future()
        value, deadline = self._cache.get(key, (None, None))
        if deadline and deadline < monotonic():
            self._cache.pop(key)
            self._cache_order.remove(key)
        f.set_result(value)
        return f

    def set(self, key, value, expires=0):
        if key in self._cache and self._cache_order[-1] != key:
            idx = self._cache_order.index(key)
            del self._cache_order[idx]
            self._cache_order.append(key)
        else:
            if len(self._cache) >= self.limit:
                oldest = self._cache_order.pop(0)
                self._cache.pop(oldest)
            self._cache_order.append(key)

        if not expires:
            deadline = None
        else:
            deadline = monotonic() + expires

        self._cache[key] = (value, deadline)
        f = Future()
        f.set_result(True)
        return f


def cached(
    cache: Cache,
    func: Callable | None = None,
    key_func: Callable | None = None,
    ttl: int | None = None,
) -> Callable:
    """
    Cache decorator with arguments.
    """

    def decorator(func: F) -> F:
        """Cache decorator for function"""

        def inner(*args, **kwargs) -> Any:
            """inner function"""
            cache_key = key_func(*args) if key_func else f"cache__{func.__name__}"
            data = cache.get(cache_key)
            if data is not None:
                return data
            result = func(*args, **kwargs)
            if result is not None:
                cache.set(cache_key, result, ttl)
            return result

        return cast(F, inner)

    if func is None:
        # decorator used like @cached(...)
        return decorator
    # decorator used like @cached, without brackets
    return decorator(func)


CACHE = SimpleCache()
