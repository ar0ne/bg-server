"""Utility functions"""
import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any
from uuid import UUID


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        return json.JSONEncoder.default(self, o)


class JsonDecoderMixin:
    """Mixin for parsing request body and convert to JSON if needed"""

    def prepare(self):
        if self.request.headers.get("Content-Type", "").startswith("application/json"):
            self.json_args = json.loads(self.request.body)
        else:
            self.json_args = None


class JsonEncoder:
    @staticmethod
    def encode(value: Any) -> str:
        return json.dumps(value, sort_keys=True, indent=1, cls=DateTimeEncoder)


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if is_dataclass(o):
            return asdict(o)
        if isinstance(o, UUID):
            return str(o)
        return super().default(o)