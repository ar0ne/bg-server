import tornado


class MainHandler(tornado.web.RequestHandler):  # type: ignore
    """Main request handler"""

    async def get(self) -> None:
        """Render index page"""
        self.render("index.html")
