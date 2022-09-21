"""Utility functions"""
import json
from typing import Any

from datetime import datetime


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
