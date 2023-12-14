"""Websocket handler"""
import logging

from tornado.websocket import WebSocketHandler

log = logging.getLogger(__name__)

# FIXME: i need to store websocket connections for each room somewhere
# FIXME: socket-io + redis-adapter


class RoomWebSocketHandler(WebSocketHandler):
    """Room websocket handler"""

    live_web_sockets = set()

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs):
        log.info("WebSocket opened")
        self.set_nodelay(True)
        self.live_web_sockets.add(self)

    def on_message(self, message: str | bytes):
        if message and message == "refresh":
            self.notify_all(message)
            return
        self.write_message(message)

    def on_close(self) -> None:
        log.info("WebSocket closed")
        if self in self.live_web_sockets:
            self.live_web_sockets.remove(self)

    @classmethod
    def notify_all(cls, message) -> None:
        removable = set()
        for ws in cls.live_web_sockets:
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                removable.add(ws)
            else:
                ws.write_message(message)
        for ws in removable:
            cls.live_web_sockets.remove(ws)
