"""Utilities"""
import json
from dataclasses import asdict, dataclass, fields
from typing import Tuple


class Serializable:
    not_serializing: Tuple = tuple()

    @classmethod
    def fromdict(cls, d):
        if d is None:
            return None
        keys = {f.name for f in fields(cls)}
        d = {k: v for k, v in d.items() if k in keys}
        return cls(**d)

    def asdict(self):
        d = asdict(self)
        for field in self.not_serializing:
            d.pop(field, None)
        d.pop("not_serializing", None)
        return d

    @classmethod
    def deserialize(cls, line):
        return cls.fromdict(json.loads(line))

    def serialize(self):
        return json.dumps(self.asdict(), ensure_ascii=False)
