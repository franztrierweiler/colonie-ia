"""
Routes d'authentification.
"""
from flask import jsonify, request
from pydantic import ValidationError

from app import db
from app.routes import api_bp
from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema, RefreshSchema
from app.services.auth import (
    hash_password,
    create_access_token,
    create_refresh_token,
    authenticate_user,
    get_user_from_token,
)
from app.utils.errors import ValidationError as APIValidationError, AuthenticationError


@api_bp.route("/auth/register", methods=["POST"])
def register():
    """Inscription d'un nouvel utilisateur."""
    try:
        data = RegisterSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400

    # Vérifier si l'email existe déjà
    existing_user = db.session.query(User).filter_by(email=data.email.lower()).first()
    if existing_user:
        return jsonify({"error": "Cet email est déjà utilisé"}), 409

    # Vérifier si le pseudo existe déjà
    existing_pseudo = db.session.query(User).filter_by(pseudo=data.pseudo).first()
    if existing_pseudo:
        return jsonify({"error": "Ce pseudo est déjà utilisé"}), 409

    # Créer l'utilisateur
    user = User(
        email=data.email.lower(),
        password_hash=hash_password(data.password),
        pseudo=data.pseudo,
    )
    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Compte créé avec succès",
        "user": {
            "id": user.id,
            "email": user.email,
            "pseudo": user.pseudo,
        }
    }), 201


@api_bp.route("/auth/login", methods=["POST"])
def login():
    """Connexion d'un utilisateur."""
    try:
        data = LoginSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400

    try:
        user = authenticate_user(data.email, data.password)
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401

    # Générer les tokens
    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "pseudo": user.pseudo,
            "avatar_url": user.avatar_url,
        }
    })


@api_bp.route("/auth/refresh", methods=["POST"])
def refresh():
    """Rafraîchir le token d'accès."""
    try:
        data = RefreshSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400

    try:
        user = get_user_from_token(data.refresh_token, token_type="refresh")
    except AuthenticationError as e:
        return jsonify({"error": str(e)}), 401

    # Générer un nouveau access token
    access_token = create_access_token(user.id)

    return jsonify({
        "access_token": access_token,
        "token_type": "bearer",
    })


@api_bp.route("/auth/logout", methods=["POST"])
def logout():
    """Déconnexion (côté client, invalider les tokens)."""
    # Pour une implémentation simple, le logout est géré côté client
    # en supprimant les tokens du localStorage.
    # Une implémentation plus robuste utiliserait une blacklist Redis.
    return jsonify({"message": "Déconnexion réussie"})


@api_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """Statut du module d'authentification."""
    return jsonify({
        "module": "auth",
        "status": "operational",
        "endpoints": [
            "POST /api/auth/register",
            "POST /api/auth/login",
            "POST /api/auth/logout",
            "POST /api/auth/refresh",
        ]
    })
