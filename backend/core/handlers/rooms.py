"""Room handlers"""
import tornado

from core.resources.auth import login_required
from core.resources.errors import APIError
from core.resources.handlers import BaseRequestHandler
from core.services import game_room_service, room_service


class GameRoomHandler(BaseRequestHandler):
    """
    Game room request handler.
    Allows to create new game room.
    """

    @login_required
    async def post(self, game_id: str) -> None:
        """Create game room"""
        room_size = self.request.arguments.get("size")
        data = await room_service.create_room(game_id, self.request.user, room_size)
        self.set_status(201)
        self.write(dict(data=data))


class RoomHandler(BaseRequestHandler):
    """
    Room request handler.
    Allows to get all available game rooms, room details, setup room (and start game).
    """

    async def get(self, room_id: str | None = None) -> None:
        if not room_id:
            # FIXME: add limit
            # FIXME: filter open to join pages only
            results = await room_service.get_available_rooms()
            data = dict(results=results)
        else:
            room = await room_service.get_room_by_id(room_id)
            data = dict(data=room)
        self.write(data)

    @login_required
    async def put(self, room_id: str) -> None:
        """Player could setup game settings"""
        user = self.request.user
        data = await room_service.update_room(room_id, user, self.request.arguments)
        # notify all users to fetch updated data
        await self.application.socket_manager.broadcast_to_room(room_id, "refresh")
        self.write(dict(data=data))


class RoomDataHandler(BaseRequestHandler):
    """
    Game Room data request handler.
    Allows to receive latest game state.
    """

    async def get(self, room_id: str) -> None:
        """Get the latest game room state"""
        user_id = str(self.request.user.id) if self.request.user else None
        data = await game_room_service.get_game_room_state(room_id, user_id)
        # wrap up in object -> {"data": {...}}
        self.write(dict(data=data))


class RoomGameTurnHandler(BaseRequestHandler):
    """
    Game Turn data request handler.
    Allows to make a game turn.
    """

    @login_required
    async def post(self, room_id: str) -> None:
        """Create a game turn"""
        user = self.request.user
        turn = self.request.arguments
        if not turn:
            raise APIError(400, "Validation error")
        data = await game_room_service.make_turn(room_id, user, turn)
        # notify all users to fetch updated data
        await self.application.socket_manager.broadcast_to_room(room_id, "refresh")
        self.write(dict(data=data))


class RoomPlayersHandler(BaseRequestHandler):
    """
    Room players request handler.
    Let add and remove room participants.
    """

    @login_required
    async def post(self, room_id: str) -> None:
        """join room"""
        player_id = self.request.arguments.get("user_id")
        current_user = self.request.user
        if str(current_user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        data = await room_service.join_room(room_id, current_user)
        # notify all users to fetch updated data
        await self.application.socket_manager.broadcast_to_room(room_id, "refresh")
        self.set_status(201)
        self.write(dict(data=data))

    @login_required
    async def delete(self, room_id: str, player_id: str) -> None:
        """Player could cancel own participation"""
        user = self.request.user
        if str(user.id) != player_id:
            raise APIError(401, "Can't perform this action.")
        await room_service.leave_room(room_id, user)
        # notify all users to fetch updated data
        await self.application.socket_manager.broadcast_to_room(room_id, "refresh")
        self.set_status(204)
