import tornado


class MainHandler(tornado.web.RequestHandler):
    """Main request handler"""

    async def get(self) -> None:
        """Render index page"""
        self.render("index.html", games=games)
