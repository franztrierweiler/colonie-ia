"""
Routes utilisateur.
"""
from functools import wraps
from flask import jsonify, request

from app.routes import api_bp
from app.services.auth import get_user_from_token
from app.utils.errors import AuthenticationError


def auth_required(f):
    """Décorateur pour exiger une authentification."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Token d'authentification requis"}), 401

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            return jsonify({"error": "Format d'authentification invalide"}), 401

        token = parts[1]

        try:
            user = get_user_from_token(token, token_type="access")
            request.current_user = user
        except AuthenticationError as e:
            return jsonify({"error": str(e)}), 401

        return f(*args, **kwargs)

    return decorated_function


@api_bp.route("/users/me", methods=["GET"])
@auth_required
def get_current_user():
    """Récupère le profil de l'utilisateur connecté."""
    user = request.current_user
    return jsonify({
        "id": user.id,
        "email": user.email,
        "pseudo": user.pseudo,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })
