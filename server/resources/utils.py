"""Utility functions"""
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