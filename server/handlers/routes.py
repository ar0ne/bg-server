"""App routing"""
from typing import List, Tuple

import tornado

from server.handlers.auth import AuthLoginHandler, AuthLogoutHandler, AuthSignUpHandler
from server.handlers.game import GameHandler
from server.handlers.index import MainHandler
from server.handlers.player import PlayerHandler
from server.handlers.room import GameRoomHandler, RoomHandler, RoomPlayersHandler


API_URL_PREFIX = "/api/v1"


def get_routes() -> List[Tuple[str, tornado.web.RequestHandler]]:
    """Create app route mapping"""
    routes = [
        (r"/auth/sign-up/?", AuthSignUpHandler),
        (r"/auth/login/?", AuthLoginHandler),
        (r"/auth/logout/?", AuthLogoutHandler),

        # FIXME: mot API
        (r"/games/(\w+)/rooms/?", GameRoomHandler),
        (r"/games/(\w+)/?", GameHandler),
        (r"/games/?", GameHandler),
        (r"/rooms/([a-zA-Z0-9_.-]+)/players/?", RoomPlayersHandler),
        (r"/rooms/([a-zA-Z0-9_.-]+)/?", RoomHandler),
        (r"/rooms/?", RoomHandler),
        (r"/players/([a-zA-Z0-9_.-]+)/?", PlayerHandler),
    ]
    routes = [(API_URL_PREFIX + url, handler) for (url, handler) in routes]
    routes.append((r"/", MainHandler))
    return routes
