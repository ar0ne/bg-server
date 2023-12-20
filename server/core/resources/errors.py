"""Error handlers"""
import json
import traceback
from typing import Any, Optional

import tornado


class AppException(tornado.web.HTTPError):
    """Base App exception class"""


class APIError(AppException):
    """Base API error"""


class Error(Exception):
    """Base error class"""


class ValidationError(Error, APIError):
    """Validation error"""

    error_code = ""
    error_message = ""

    def __init__(
        self,
        status_code: int = 400,
        log_message: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> None:
        super().__init__(status_code, log_message, *args, **kwargs)
        if not self.reason:
            self.reason = self.error_message


class LoaderNotFound(Error):
    """Loader function not found"""


class ErrorHandler(tornado.web.RequestHandler):
    """
    Default handler gonna to be used in case of 404 error
    """

    def initialize(self, status_code: Optional[int] = None) -> None:
        """Override initialize"""
        self.status_code = status_code

    def write_error(self, status_code: int, **kwargs) -> None:
        data = {
            "error": {
                "code": status_code,
                "message": self._reason,
            }
        }
        if "exc_info" in kwargs:
            # add error_code if possible
            exception = kwargs["exc_info"][1]
            if isinstance(exception, ValidationError) and exception.error_code:
                data["error"]["error_code"] = exception.error_code
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            lines = []
            for line in traceback.format_exception(*kwargs["exc_info"]):
                lines.append(line)
            data["error"]["traceback"] = lines
        self.finish(json.dumps(data))
