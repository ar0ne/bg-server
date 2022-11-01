"""Error handlers"""
import json
import traceback
from typing import Optional

import tornado


class AppException(tornado.web.HTTPError):
    """Base App exception class"""

    pass


class APIError(AppException):
    """Base API error"""

    pass


class ErrorHandler(tornado.web.RequestHandler):
    """
    Default handler gonna to be used in case of 404 error
    """

    def initialize(self, status_code: Optional[int] = None) -> None:
        """Override initialize"""
        self.status_code = status_code

    def write_error(self, status_code: int, **kwargs) -> None:

        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            self.finish(
                json.dumps(
                    {
                        "error": {
                            "code": status_code,
                            "message": self._reason,
                            "traceback": lines,
                        }
                    }
                )
            )
        else:
            self.finish(
                json.dumps(
                    {
                        "error": {
                            "code": status_code,
                            "message": self._reason,
                        }
                    }
                )
            )
