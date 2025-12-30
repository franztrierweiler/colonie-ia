"""
Routes OAuth (Google).
"""
from flask import jsonify, request, redirect, current_app, url_for
from authlib.integrations.requests_client import OAuth2Session

from app import db
from app.routes import api_bp
from app.models.user import User
from app.services.auth import create_access_token, create_refresh_token


GOOGLE_AUTHORIZE_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def get_google_client():
    """Crée un client OAuth2 pour Google."""
    return OAuth2Session(
        client_id=current_app.config["GOOGLE_CLIENT_ID"],
        client_secret=current_app.config["GOOGLE_CLIENT_SECRET"],
        redirect_uri=current_app.config["GOOGLE_REDIRECT_URI"],
    )


@api_bp.route("/auth/google", methods=["GET"])
def google_login():
    """
    Initie la connexion OAuth Google
    ---
    tags:
      - OAuth
    description: |
      Redirige vers la page de connexion Google.
      Après authentification, l'utilisateur est redirigé vers /api/auth/google/callback
    responses:
      302:
        description: Redirection vers Google
    """
    if not current_app.config.get("GOOGLE_CLIENT_ID"):
        return jsonify({"error": "OAuth Google non configuré"}), 501

    client = get_google_client()
    uri, state = client.create_authorization_url(
        GOOGLE_AUTHORIZE_URL,
        scope="openid email profile",
    )

    # Stocker le state en session (ou cookie) pour validation
    # Pour simplifier, on le retourne dans l'URL
    return redirect(uri)


@api_bp.route("/auth/google/callback", methods=["GET"])
def google_callback():
    """
    Callback OAuth Google
    ---
    tags:
      - OAuth
    parameters:
      - in: query
        name: code
        type: string
        required: true
        description: Code d'autorisation retourné par Google
      - in: query
        name: state
        type: string
        description: State pour validation CSRF
    responses:
      302:
        description: Redirection vers le frontend avec les tokens
      400:
        description: Erreur d'authentification
    """
    if not current_app.config.get("GOOGLE_CLIENT_ID"):
        return jsonify({"error": "OAuth Google non configuré"}), 501

    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Code d'autorisation manquant"}), 400

    try:
        client = get_google_client()

        # Échanger le code contre un token
        token = client.fetch_token(
            GOOGLE_TOKEN_URL,
            authorization_response=request.url,
        )

        # Récupérer les infos utilisateur
        client.token = token
        resp = client.get(GOOGLE_USERINFO_URL)
        userinfo = resp.json()

        google_id = userinfo.get("sub")
        email = userinfo.get("email")
        name = userinfo.get("name", "")
        picture = userinfo.get("picture", "")

        if not email:
            return jsonify({"error": "Email non fourni par Google"}), 400

        # Chercher ou créer l'utilisateur
        user = db.session.query(User).filter(
            (User.oauth_provider == "google") & (User.oauth_id == google_id) |
            (User.email == email.lower())
        ).first()

        if user:
            # Utilisateur existant - mettre à jour les infos OAuth si nécessaire
            if not user.oauth_provider:
                user.oauth_provider = "google"
                user.oauth_id = google_id
            if not user.avatar_url and picture:
                user.avatar_url = picture
            user.is_verified = True
            db.session.commit()
        else:
            # Nouvel utilisateur
            # Générer un pseudo unique à partir du nom
            base_pseudo = name.replace(" ", "") if name else email.split("@")[0]
            pseudo = base_pseudo[:20]

            # Vérifier unicité du pseudo
            counter = 1
            while db.session.query(User).filter_by(pseudo=pseudo).first():
                pseudo = f"{base_pseudo[:17]}{counter}"
                counter += 1

            user = User(
                email=email.lower(),
                pseudo=pseudo,
                avatar_url=picture,
                oauth_provider="google",
                oauth_id=google_id,
                is_verified=True,
            )
            db.session.add(user)
            db.session.commit()

        # Générer les tokens JWT
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        # Rediriger vers le frontend avec les tokens
        frontend_url = current_app.config.get("CORS_ORIGINS", ["http://localhost:5173"])[0]
        redirect_url = f"{frontend_url}/oauth/callback?access_token={access_token}&refresh_token={refresh_token}"

        return redirect(redirect_url)

    except Exception as e:
        current_app.logger.error(f"Erreur OAuth Google: {e}")
        return jsonify({"error": "Erreur lors de l'authentification Google"}), 400


@api_bp.route("/auth/google/status", methods=["GET"])
def google_oauth_status():
    """
    Vérifie si OAuth Google est configuré
    ---
    tags:
      - OAuth
    responses:
      200:
        description: Statut de la configuration OAuth
        schema:
          type: object
          properties:
            enabled:
              type: boolean
            provider:
              type: string
    """
    enabled = bool(current_app.config.get("GOOGLE_CLIENT_ID"))
    return jsonify({
        "enabled": enabled,
        "provider": "google",
    })
