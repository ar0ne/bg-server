"""
Main
"""
import asyncio
import os

import tornado.web

from tornado.options import define, options, parse_command_line

define("port", default=8888, help="run on the given port", type=int)
define("debug", default=True, help="run in debug mode")


class MainHandler(tornado.web.RequestHandler):
    """Main request handler"""

    def get(self) -> None:
        self.write("hello")


async def main() -> None:
    """Main loop function"""

    parse_command_line()

    app = tornado.web.Application(
        [
            (r"/", MainHandler),
        ],
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        debug=options.debug,
    )
    app.listen(options.port)
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())
