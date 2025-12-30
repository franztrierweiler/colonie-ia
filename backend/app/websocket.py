"""
WebSocket events for real-time game communication.
"""
from flask import request
from flask_socketio import emit, join_room, leave_room, disconnect

from app import socketio
from app.services.auth import get_user_from_token
from app.utils.errors import AuthenticationError


# Store connected users: {sid: user_id}
connected_users = {}


@socketio.on("connect")
def handle_connect(auth=None):
    """Handle client connection with JWT authentication."""
    token = None

    # Try to get token from auth data
    if auth and isinstance(auth, dict):
        token = auth.get("token")

    # Or from query string
    if not token:
        token = request.args.get("token")

    if not token:
        print(f"[WS] Connection rejected: no token provided")
        disconnect()
        return False

    try:
        user = get_user_from_token(token, token_type="access")
        connected_users[request.sid] = {
            "user_id": user.id,
            "pseudo": user.pseudo,
        }
        print(f"[WS] User {user.pseudo} connected (sid: {request.sid})")
        emit("connected", {"message": f"Bienvenue, {user.pseudo}!"})
        return True
    except AuthenticationError as e:
        print(f"[WS] Connection rejected: {e}")
        disconnect()
        return False


@socketio.on("disconnect")
def handle_disconnect():
    """Handle client disconnection."""
    user_info = connected_users.pop(request.sid, None)
    if user_info:
        print(f"[WS] User {user_info['pseudo']} disconnected")


@socketio.on("join_game")
def handle_join_game(data):
    """Join a game room."""
    game_id = data.get("game_id")
    user_info = connected_users.get(request.sid)

    if not user_info:
        emit("error", {"message": "Non authentifié"})
        return

    if not game_id:
        emit("error", {"message": "game_id requis"})
        return

    room = f"game_{game_id}"
    join_room(room)

    print(f"[WS] User {user_info['pseudo']} joined game {game_id}")

    # Notify the user
    emit("game_joined", {
        "game_id": game_id,
        "message": f"Vous avez rejoint la partie {game_id}"
    })

    # Notify other players in the room
    emit("player_joined", {
        "user_id": user_info["user_id"],
        "pseudo": user_info["pseudo"],
    }, room=room, include_self=False)


@socketio.on("leave_game")
def handle_leave_game(data):
    """Leave a game room."""
    game_id = data.get("game_id")
    user_info = connected_users.get(request.sid)

    if not user_info:
        return

    if not game_id:
        emit("error", {"message": "game_id requis"})
        return

    room = f"game_{game_id}"

    # Notify other players before leaving
    emit("player_left", {
        "user_id": user_info["user_id"],
        "pseudo": user_info["pseudo"],
    }, room=room, include_self=False)

    leave_room(room)
    print(f"[WS] User {user_info['pseudo']} left game {game_id}")

    emit("game_left", {
        "game_id": game_id,
        "message": f"Vous avez quitté la partie {game_id}"
    })


@socketio.on("chat_message")
def handle_chat_message(data):
    """Handle chat message in a game room."""
    game_id = data.get("game_id")
    message = data.get("message", "").strip()
    user_info = connected_users.get(request.sid)

    if not user_info:
        emit("error", {"message": "Non authentifié"})
        return

    if not game_id:
        emit("error", {"message": "game_id requis"})
        return

    if not message:
        return

    # Limit message length
    if len(message) > 500:
        message = message[:500]

    room = f"game_{game_id}"

    # Broadcast to all players in the room
    emit("chat_message", {
        "user_id": user_info["user_id"],
        "pseudo": user_info["pseudo"],
        "message": message,
    }, room=room)


# Utility functions for emitting from outside handlers

def emit_game_update(game_id: int, data: dict):
    """Emit game state update to all players in a game."""
    room = f"game_{game_id}"
    socketio.emit("game_update", data, room=room)


def emit_turn_end(game_id: int, data: dict):
    """Emit turn end notification to all players in a game."""
    room = f"game_{game_id}"
    socketio.emit("turn_end", data, room=room)


def emit_to_user(user_id: int, event: str, data: dict):
    """Emit event to a specific user."""
    for sid, info in connected_users.items():
        if info["user_id"] == user_id:
            socketio.emit(event, data, room=sid)
            break
