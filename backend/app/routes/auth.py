"""
Routes d'authentification.
"""
from flask import jsonify, request
from pydantic import ValidationError

from app import db, limiter
from app.routes import api_bp
from app.models.user import User
from app.schemas.auth import RegisterSchema, LoginSchema, RefreshSchema
from app.services.auth import (
    hash_password,
    create_access_token,
    create_refresh_token,
    authenticate_user,
    get_user_from_token,
    generate_reset_token,
    verify_reset_token,
)
from app.utils.errors import ValidationError as APIValidationError, AuthenticationError
from app.schemas.auth import ForgotPasswordSchema, ResetPasswordSchema


@api_bp.route("/auth/register", methods=["POST"])
@limiter.limit("5 per hour")
def register():
    """
    Inscription d'un nouvel utilisateur
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
            - pseudo
          properties:
            email:
              type: string
              format: email
              example: joueur@example.com
            password:
              type: string
              minLength: 8
              example: MonMotDePasse123
            pseudo:
              type: string
              minLength: 3
              maxLength: 30
              example: GeneralNapoleon
    responses:
      201:
        description: Compte créé avec succès
        schema:
          type: object
          properties:
            message:
              type: string
            user:
              type: object
              properties:
                id:
                  type: integer
                email:
                  type: string
                pseudo:
                  type: string
      400:
        description: Erreur de validation
      409:
        description: Email ou pseudo déjà utilisé
      429:
        description: Trop de requêtes (rate limit)
    """
    try:
        data = RegisterSchema(**request.get_json())
    except ValidationError as e:
        # Convert errors to JSON-serializable format
        errors = []
        for err in e.errors():
            errors.append({
                "loc": err.get("loc", []),
                "msg": err.get("msg", ""),
                "type": err.get("type", "")
            })
        return jsonify({"error": "Validation error", "details": errors}), 400

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
@limiter.limit("5 per 5 minutes")
def login():
    """
    Connexion d'un utilisateur
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
            - password
          properties:
            email:
              type: string
              format: email
              example: joueur@example.com
            password:
              type: string
              example: MonMotDePasse123
    responses:
      200:
        description: Connexion réussie
        schema:
          type: object
          properties:
            access_token:
              type: string
              description: JWT access token (15 min)
            refresh_token:
              type: string
              description: JWT refresh token (7 jours)
            token_type:
              type: string
              example: bearer
            user:
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
      400:
        description: Erreur de validation
      401:
        description: Email ou mot de passe incorrect
      429:
        description: Trop de tentatives (rate limit)
    """
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
@limiter.limit("30 per hour")
def refresh():
    """
    Rafraîchir le token d'accès
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - refresh_token
          properties:
            refresh_token:
              type: string
              description: Le refresh token obtenu lors du login
    responses:
      200:
        description: Nouveau access token généré
        schema:
          type: object
          properties:
            access_token:
              type: string
            token_type:
              type: string
              example: bearer
      400:
        description: Erreur de validation
      401:
        description: Refresh token invalide ou expiré
      429:
        description: Trop de requêtes (rate limit)
    """
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
    """
    Déconnexion de l'utilisateur
    ---
    tags:
      - Authentification
    responses:
      200:
        description: Déconnexion réussie
        schema:
          type: object
          properties:
            message:
              type: string
              example: Déconnexion réussie
    """
    # Pour une implémentation simple, le logout est géré côté client
    # en supprimant les tokens du localStorage.
    # Une implémentation plus robuste utiliserait une blacklist Redis.
    return jsonify({"message": "Déconnexion réussie"})


@api_bp.route("/auth/forgot-password", methods=["POST"])
@limiter.limit("3 per hour")
def forgot_password():
    """
    Demande de réinitialisation du mot de passe
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - email
          properties:
            email:
              type: string
              format: email
              example: joueur@example.com
    responses:
      200:
        description: Email envoyé (toujours retourné pour éviter l'énumération)
        schema:
          type: object
          properties:
            message:
              type: string
      429:
        description: Trop de requêtes
    """
    from flask import current_app
    from datetime import datetime, timedelta

    try:
        data = ForgotPasswordSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400

    # Toujours retourner succès pour éviter l'énumération des emails
    user = db.session.query(User).filter_by(email=data.email.lower()).first()

    if user and user.is_active:
        # Générer le token de réinitialisation
        reset_token = generate_reset_token()
        user.reset_token = reset_token
        user.reset_token_expires = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

        # En production, envoyer un email
        # Pour le dev, on log le token
        frontend_url = current_app.config.get("CORS_ORIGINS", ["http://localhost:5173"])[0]
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        current_app.logger.info(f"Reset password URL for {user.email}: {reset_url}")

        # TODO: Intégrer SendGrid ou SMTP pour envoyer l'email
        # send_reset_email(user.email, reset_url)

    return jsonify({
        "message": "Si un compte existe avec cet email, un lien de réinitialisation a été envoyé."
    })


@api_bp.route("/auth/reset-password", methods=["POST"])
@limiter.limit("5 per hour")
def reset_password():
    """
    Réinitialise le mot de passe avec le token
    ---
    tags:
      - Authentification
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - token
            - password
          properties:
            token:
              type: string
              description: Token reçu par email
            password:
              type: string
              minLength: 8
              description: Nouveau mot de passe
    responses:
      200:
        description: Mot de passe réinitialisé
        schema:
          type: object
          properties:
            message:
              type: string
      400:
        description: Token invalide ou expiré
      429:
        description: Trop de requêtes
    """
    from datetime import datetime

    try:
        data = ResetPasswordSchema(**request.get_json())
    except ValidationError as e:
        return jsonify({"error": "Validation error", "details": e.errors()}), 400

    # Vérifier le token
    user = verify_reset_token(data.token)
    if not user:
        return jsonify({"error": "Token invalide ou expiré"}), 400

    # Mettre à jour le mot de passe
    user.password_hash = hash_password(data.password)
    user.reset_token = None
    user.reset_token_expires = None
    db.session.commit()

    return jsonify({
        "message": "Mot de passe réinitialisé avec succès. Vous pouvez maintenant vous connecter."
    })


@api_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """
    Statut du module d'authentification
    ---
    tags:
      - Système
    responses:
      200:
        description: Statut du module
        schema:
          type: object
          properties:
            module:
              type: string
            status:
              type: string
            endpoints:
              type: array
              items:
                type: string
    """
    return jsonify({
        "module": "auth",
        "status": "operational",
        "endpoints": [
            "POST /api/auth/register",
            "POST /api/auth/login",
            "POST /api/auth/logout",
            "POST /api/auth/refresh",
            "POST /api/auth/forgot-password",
            "POST /api/auth/reset-password",
        ]
    })
