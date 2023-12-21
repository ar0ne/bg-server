from typing import Any, Dict

import tornado

from tornado.escape import json_decode

from core.resources.auth import JWTAuthMiddleware
from core.resources.errors import ErrorHandler


class BaseRequestHandler(JWTAuthMiddleware, ErrorHandler, tornado.web.RequestHandler):
    """Base request handler"""

    def set_default_headers(self) -> None:
        # enable CORS
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header(
            "Access-Control-Allow-Headers",
            "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With",
        )
        self.set_header("Access-Control-Allow-Methods", " POST, PUT, GET, DELETE, OPTIONS")
        self.set_header("Content-Type", "application/json")

    async def prepare(self) -> None:
        """Prepare request"""
        if self.request.body:
            try:
                json_body = json_decode(self.request.body)
                self.request.arguments.update(json_body)
            except ValueError:
                message = "Unable to parse JSON."
                self.send_error(400, message=message)  # Bad Request

        # Set up response dictionary.
        self.response: Dict[str, Any] = dict()

    async def options(self, *args, **kwargs) -> None:
        """Handle OPTIONS method"""
        pass
