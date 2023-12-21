"""Utility functions"""
import importlib.util
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


def lazy_import(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    # creates a new module based on spec
    module = importlib.util.module_from_spec(spec)
    # executes the module in its own namespace
    # when a module is imported or reloaded.
    spec.loader.exec_module(module)
    return module
