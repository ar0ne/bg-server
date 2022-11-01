"""Auth handlers"""
import bcrypt
import tornado
from tortoise.expressions import Q

from resources.errors import APIError
from server.resources.auth import get_jwt_token
from server.resources.models import Player
from server.resources.handlers import BaseRequestHandler


class AuthSignUpHandler(BaseRequestHandler):
    """Sign Up handler"""

    async def post(self) -> None:
        data = self.request.arguments
        username, email, password = data["username"], data["email"], data["password"]

        # FIXME: add better validation
        if not (username and email and password):
            raise APIError(status_code=400, reason="Invalid data")

        if await Player.exists(Q(email=email) | Q(name=username)):
            raise APIError(status_code=400, reason="Player with this email or name already registered.")

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.hashpw,
            tornado.escape.utf8(password),
            bcrypt.gensalt(),
        )
        await Player.create(
            email=email,
            name=username,
            password=tornado.escape.to_unicode(hashed_password),
        )
        self.set_status(204)


class AuthLoginHandler(BaseRequestHandler):
    """Login handler"""

    async def post(self):
        username, password = self.request.arguments["name"], self.request.arguments["password"]
        player = await Player.filter(name=username).first()
        if not player:
            raise APIError(status_code=400, reason="Incorrect user or password.")
        password_equal = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.checkpw,
            tornado.escape.utf8(password),
            tornado.escape.utf8(player.password),
        )
        if not password_equal:
            raise APIError(status_code=400, reason="Incorrect user or password.")

        user_id = str(player.id)
        self.write({
            "user_id": user_id,
            "token": await get_jwt_token(user_id),
        })
