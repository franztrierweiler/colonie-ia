"""
Service d'authentification : hashage de mot de passe et gestion JWT.
"""
import jwt
from datetime import datetime, timedelta, timezone
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from flask import current_app

from app.models.user import User
from app.utils.errors import AuthenticationError

# Instance du hasher Argon2
ph = PasswordHasher()


def hash_password(password: str) -> str:
    """Hash un mot de passe avec Argon2."""
    return ph.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Vérifie un mot de passe contre son hash."""
    try:
        ph.verify(password_hash, password)
        return True
    except VerifyMismatchError:
        return False


def create_access_token(user_id: int) -> str:
    """Crée un access token JWT."""
    expires = datetime.now(timezone.utc) + current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
    payload = {
        "sub": str(user_id),
        "type": "access",
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def create_refresh_token(user_id: int) -> str:
    """Crée un refresh token JWT."""
    expires = datetime.now(timezone.utc) + current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expires,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, current_app.config["JWT_SECRET_KEY"], algorithm="HS256")


def decode_token(token: str) -> dict:
    """Décode et valide un token JWT."""
    try:
        payload = jwt.decode(
            token,
            current_app.config["JWT_SECRET_KEY"],
            algorithms=["HS256"]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationError("Token expiré")
    except jwt.InvalidTokenError:
        raise AuthenticationError("Token invalide")


def get_user_from_token(token: str, token_type: str = "access") -> User:
    """Récupère l'utilisateur à partir d'un token."""
    payload = decode_token(token)

    if payload.get("type") != token_type:
        raise AuthenticationError(f"Type de token invalide, attendu: {token_type}")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise AuthenticationError("Token invalide: pas d'identifiant utilisateur")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise AuthenticationError("Token invalide: identifiant utilisateur malformé")

    from app import db
    user = db.session.get(User, user_id)

    if not user:
        raise AuthenticationError("Utilisateur non trouvé")

    if not user.is_active:
        raise AuthenticationError("Compte désactivé")

    if user.is_deleted:
        raise AuthenticationError("Compte supprimé")

    return user


def authenticate_user(email: str, password: str) -> User:
    """Authentifie un utilisateur par email/mot de passe."""
    from app import db

    user = db.session.query(User).filter_by(email=email.lower()).first()

    if not user:
        raise AuthenticationError("Email ou mot de passe incorrect")

    if not user.password_hash:
        raise AuthenticationError("Ce compte utilise une connexion OAuth")

    if not verify_password(password, user.password_hash):
        raise AuthenticationError("Email ou mot de passe incorrect")

    if not user.is_active:
        raise AuthenticationError("Compte désactivé")

    if user.is_deleted:
        raise AuthenticationError("Compte supprimé")

    return user
