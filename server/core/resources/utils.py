"""Utility functions"""
import importlib
import json

from dataclasses import asdict, is_dataclass
from uuid import UUID


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)


def load_module(module_name: str):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        log.warning("Can't import module (%s)", module_name)
    return None
