"""
Main
"""
import asyncio
import os

from aiocache import caches
from tornado import web
from tornado.options import options

from core.config import ROOT_PATH, STATIC_PATH, TEMPLATE_PATH
from core.database import init_database
from core.handlers.routes import get_routes
from core.resources.errors import ErrorHandler
from core.websocket import RedisPubSubManager, WebSocketManager


class Application(web.Application):
    """Application"""

    def __init__(self, db, cache, socket_manager):
        """Init application"""
        self.db = db
        self.cache = cache
        self.socket_manager = socket_manager
        settings = dict(
            debug=options.debug,
            static_path=STATIC_PATH,
            template_path=TEMPLATE_PATH,
            default_handler_class=ErrorHandler,
            default_handler_args=dict(status_code=404),
        )
        routes = get_routes()
        super().__init__(routes, **settings)


async def main() -> None:
    """Main loop function"""
    await init_database()
    cache = caches.get("default")
    pubsub = RedisPubSubManager(options.redis_host, options.redis_port)
    socket_manager = WebSocketManager(pubsub)
    app = Application(None, cache, socket_manager)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
