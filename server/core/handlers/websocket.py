"""Websocket handler"""
import logging

from tornado.websocket import WebSocketHandler

log = logging.getLogger(__name__)


class EchoWebSocket(WebSocketHandler):
    def check_origin(self, origin):
        return True

    def open(self):
        log.info("WebSocket opened")

    def on_message(self, message):
        self.write_message("You said: " + message)

    def on_close(self):
        log.info("WebSocket closed")
