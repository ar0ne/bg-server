import tornado

from server.resources.models import Player
from server.resources.utils import JsonDecoderMixin
from server.constants import COOKIE_USER_KEY


class BaseRequestHandler(tornado.web.RequestHandler):
    """Base request handler"""

    def set_default_headers(self):
        # enable CORS
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header("Access-Control-Allow-Methods", "PUT, DELETE, OPTIONS")
        self.set_header("Content-Type", "application/json")

    async def prepare(self):
        # get_current_user cannot be a coroutine, so set
        # self.current_user in prepare instead.
        if self.current_user:
            return
        user_id = self.get_secure_cookie(COOKIE_USER_KEY)
        if not user_id:
            return
        self.current_user = await Player.filter(id=user_id.decode("utf-8")).first()
