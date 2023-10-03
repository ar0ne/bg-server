"""App routing"""
from typing import List, Tuple

import tornado
from core.handlers.auth import AuthLoginHandler, AuthSignUpHandler
from core.handlers.game import GameHandler
from core.handlers.index import MainHandler
from core.handlers.player import PlayerHandler
from core.handlers.room import GameRoomHandler, RoomDataHandler, RoomHandler, RoomPlayersHandler

API_URL_PREFIX = "/api/v1"


def get_routes() -> List[Tuple[str, tornado.web.RequestHandler]]:
    """Create app route mapping"""
    routes = [
        (r"/auth/sign-up/?", AuthSignUpHandler),
        (r"/auth/login/?", AuthLoginHandler),
        (r"/games/([a-zA-Z0-9_.-]+)/rooms/?", GameRoomHandler),
        (r"/games/([a-zA-Z0-9_.-]+)/?", GameHandler),
        (r"/games/?", GameHandler),
        (r"/players/([a-zA-Z0-9_.-]+)/?", PlayerHandler),
        (r"/rooms/([a-zA-Z0-9_.-]+)/?", RoomHandler),
        (r"/rooms/?", RoomHandler),
        (r"/rooms/([a-zA-Z0-9_.-]+)/data/?", RoomDataHandler),
        (r"/rooms/([a-zA-Z0-9_.-]+)/players/([a-zA-Z0-9_.-]+)/?", RoomPlayersHandler),
        (r"/rooms/([a-zA-Z0-9_.-]+)/players/?", RoomPlayersHandler),
    ]
    routes = [(API_URL_PREFIX + url, handler) for (url, handler) in routes]
    routes.append((r"/", MainHandler))
    return routes
