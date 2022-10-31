from tornado.httpclient import HTTPError
from tornado.options import options
from tornado_middleware import MiddlewareHandler

from datetime import datetime, timedelta
import jwt

from server.resources.models import Player


async def get_jwt_token(user_id: str) -> str:
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(
            seconds=int(options.JWT_EXP_DELTA_SECONDS))
    }

    jwt_token = jwt.encode(payload, options.JWT_SECRET,
                           options.JWT_ALGORITHM)
    return jwt_token


class JWTAuthMiddleware(MiddlewareHandler):
    """JWT auth middleware"""

    async def middleware_jwt(self, next):
        """Authenticate user"""
        self.request.user = None
        jwt_token = self.request.headers.get("authorization", None)
        if jwt_token:
            try:
                payload = jwt.decode(jwt_token, options.JWT_SECRET,
                                     algorithms=[options.JWT_ALGORITHM])
                self.request.user = await Player.filter(id=payload["user_id"]).first()
            except (jwt.DecodeError, jwt.ExpiredSignatureError):
                raise
        await next()


def login_required(func):
    """Decorator to verify user is logged in"""

    def wrapper(request):
        if not request.user:
            raise HTTPError(401, "Login required")
        return func(request)

    return wrapper

