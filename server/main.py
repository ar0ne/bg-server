"""
Main
"""
import asyncio
import os

from tornado import web
from tornado.options import options

from core.config import ROOT_PATH, init_options, load_env_variables
from core.database import init_database
from core.handlers.routes import get_routes
from core.resources.errors import ErrorHandler


class Application(web.Application):
    """Application"""

    def __init__(self, db):
        """Init application"""
        self.db = db
        settings = dict(
            debug=options.debug,
            static_path=os.path.join(ROOT_PATH, "static"),
            template_path=os.path.join(ROOT_PATH, "templates"),
            default_handler_class=ErrorHandler,
            default_handler_args=dict(status_code=404),
        )
        routes = get_routes()
        super().__init__(routes, **settings)


async def main() -> None:
    """Main loop function"""
    init_options()
    load_env_variables()

    await init_database()

    app = Application(None)
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
