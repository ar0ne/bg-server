"""Websocket handler"""
import logging

from tornado.websocket import WebSocketHandler

log = logging.getLogger(__name__)

# FIXME: Use something like socket-io + redis-adapter to share connections between app instances


class RoomWebSocketHandler(WebSocketHandler):
    """Room websocket handler"""

    live_web_sockets: dict = {}

    def check_origin(self, origin):
        return True

    def open(self, *args, **kwargs) -> None:
        self.set_nodelay(True)
        if not args:
            return
        if room_id := args[0]:
            if room_id not in self.live_web_sockets:
                self.live_web_sockets[room_id] = set()
            if self not in self.live_web_sockets[room_id]:
                self.live_web_sockets[room_id].add(self)

    def on_message(self, message: str | bytes) -> None:
        if message and message == "refresh" and self.open_args:
            if room_id := self.open_args[0]:
                self.notify_all_in_room(room_id, message)
            return
        self.write_message(message)

    def on_close(self) -> None:
        if not self.open_args:
            return
        if room_id := self.open_args[0]:
            if room_id in self.live_web_sockets and self in self.live_web_sockets[room_id]:
                self.live_web_sockets[room_id].remove(self)

    @classmethod
    def notify_all_in_room(cls, room_id: str, message: str | bytes) -> None:
        removable = set()
        for ws in cls.live_web_sockets[room_id]:
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                # remove not active connections
                removable.add(ws)
            else:
                ws.write_message(message)
        for ws in removable:
            cls.live_web_sockets[room_id].remove(ws)
