"""
Routes utilisateur.
"""
from functools import wraps
from flask import jsonify, request
from pydantic import ValidationError

from app.routes import api_bp
from app.services.auth import get_user_from_token
from app.schemas.auth import UpdateProfileSchema
from app.utils.errors import AuthenticationError, ValidationError as APIValidationError


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
    """
    Récupère le profil de l'utilisateur connecté
    ---
    tags:
      - Utilisateur
    security:
      - Bearer: []
    responses:
      200:
        description: Profil utilisateur
        schema:
          type: object
          properties:
            id:
              type: integer
            email:
              type: string
            pseudo:
              type: string
            avatar_url:
              type: string
            is_verified:
              type: boolean
            created_at:
              type: string
              format: date-time
      401:
        description: Non authentifié
    """
    user = request.current_user
    return jsonify({
        "id": user.id,
        "email": user.email,
        "pseudo": user.pseudo,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })


@api_bp.route("/users/me", methods=["PATCH"])
@auth_required
def update_current_user():
    """
    Met à jour le profil de l'utilisateur connecté
    ---
    tags:
      - Utilisateur
    security:
      - Bearer: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            pseudo:
              type: string
              minLength: 3
              maxLength: 30
              example: NouveauPseudo
            avatar_url:
              type: string
              format: uri
              example: https://example.com/avatar.jpg
    responses:
      200:
        description: Profil mis à jour
        schema:
          type: object
          properties:
            id:
              type: integer
            email:
              type: string
            pseudo:
              type: string
            avatar_url:
              type: string
            is_verified:
              type: boolean
            created_at:
              type: string
              format: date-time
      400:
        description: Données invalides
      401:
        description: Non authentifié
    """
    from app import db

    try:
        data = UpdateProfileSchema(**request.get_json())
    except ValidationError as e:
        errors = e.errors()
        if errors:
            return jsonify({"error": errors[0]["msg"]}), 400
        return jsonify({"error": "Données invalides"}), 400

    user = request.current_user
    updated = False

    if data.pseudo is not None:
        user.pseudo = data.pseudo
        updated = True

    if data.avatar_url is not None:
        user.avatar_url = data.avatar_url
        updated = True

    if updated:
        db.session.commit()

    return jsonify({
        "id": user.id,
        "email": user.email,
        "pseudo": user.pseudo,
        "avatar_url": user.avatar_url,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    })


@api_bp.route("/users/me", methods=["DELETE"])
@auth_required
def delete_current_user():
    """
    Supprime le compte de l'utilisateur (RGPD)
    ---
    tags:
      - Utilisateur
    security:
      - Bearer: []
    description: |
      Effectue un soft delete du compte :
      - Anonymise les données personnelles (email, pseudo)
      - Supprime le mot de passe et l'avatar
      - Marque le compte comme inactif
      - Les données seront définitivement supprimées après 30 jours
    responses:
      200:
        description: Compte supprimé et anonymisé
        schema:
          type: object
          properties:
            message:
              type: string
              example: Compte supprimé avec succès. Vos données ont été anonymisées.
      401:
        description: Non authentifié
    """
    from datetime import datetime
    import uuid
    from app import db

    user = request.current_user

    # Soft delete: anonymize data and mark as deleted
    user.email = f"deleted_{uuid.uuid4().hex[:8]}@deleted.local"
    user.pseudo = f"Utilisateur supprimé"
    user.password_hash = None
    user.avatar_url = None
    user.oauth_provider = None
    user.oauth_id = None
    user.is_active = False
    user.deleted_at = datetime.utcnow()
    user.reset_token = None
    user.reset_token_expires = None

    db.session.commit()

    return jsonify({
        "message": "Compte supprimé avec succès. Vos données ont été anonymisées."
    })
