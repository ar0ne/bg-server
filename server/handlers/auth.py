"""Auth handlers"""
import bcrypt
import tornado

from resources.jwt import get_jwt_token
from server.resources.models import Player
from server.constants import COOKIE_USER_KEY
from server.handlers.base import BaseRequestHandler


class AuthSignUpHandler(BaseRequestHandler):
    """Sign Up handler"""
    async def get(self) -> None:
        """render sign up page"""
        await self.render("sign_up.html")

    async def post(self) -> None:
        email = self.get_argument("email")
        # validation ?
        if await Player.exists(email=email):
            raise tornado.web.HTTPError(400, "player with email %s already registered" % email)

        hashed_password = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.hashpw,
            tornado.escape.utf8(self.get_argument("password")),
            bcrypt.gensalt(),
        )
        await Player.create(
            email=email,
            nickname=self.get_argument("nickname"),
            password=tornado.escape.to_unicode(hashed_password),
        )
        self.redirect(self.get_argument("next", "/"))


class AuthLoginHandler(BaseRequestHandler):
    """Login handler"""

    async def post(self):
        username, password = self.request.arguments["name"], self.request.arguments["password"]
        player = await Player.filter(name=username).first()
        if not player:
            self.set_status(400)
            self.write({"error": "Incorrect user or password!"})
            return
        password_equal = await tornado.ioloop.IOLoop.current().run_in_executor(
            None,
            bcrypt.checkpw,
            tornado.escape.utf8(password),
            tornado.escape.utf8(player.password),
        )
        if password_equal:
            self.write({"token": await get_jwt_token(str(player.id))})
        else:
            self.set_status(400)
            self.write({"error": "Incorrect user or password!"})


class AuthLogoutHandler(BaseRequestHandler):
    """Log Out handler"""
    def get(self):
        self.clear_cookie(COOKIE_USER_KEY)
        self.redirect(self.get_argument("next", "/"))

