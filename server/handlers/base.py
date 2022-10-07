import tornado

from server.app.models import Player
from server.app.utils import JsonDecoderMixin
from server.constants import COOKIE_USER_KEY


class BaseRequestHandler(JsonDecoderMixin, tornado.web.RequestHandler):
    """Base request handler"""

    async def prepare(self):
        # get_current_user cannot be a coroutine, so set
        # self.current_user in prepare instead.
        if self.current_user:
            return
        user_id = self.get_secure_cookie(COOKIE_USER_KEY)
        if not user_id:
            return
        self.current_user = await Player.filter(id=user_id.decode("utf-8")).first()
