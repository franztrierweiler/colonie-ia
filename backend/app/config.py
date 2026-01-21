"""
Configuration par environnement (dev/staging/prod)
"""
import os
import secrets
from datetime import timedelta


def _get_secret_key():
    """Get SECRET_KEY from environment or generate a random one for development.

    WARNING: If no SECRET_KEY is set, a random key is generated. This means
    sessions/tokens will be invalidated on every restart. Always set SECRET_KEY
    in production via environment variable.
    """
    key = os.environ.get("SECRET_KEY")
    if key:
        return key
    # Generate a secure random key for development (32 bytes = 256 bits)
    return secrets.token_hex(32)


class Config:
    """Configuration de base."""

    SECRET_KEY = _get_secret_key()

    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=15)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=7)

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173").split(",")

    # Rate limiting
    RATELIMIT_ENABLED = True
    RATELIMIT_DEFAULT = "100/minute"

    # Password policy
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPERCASE = True
    PASSWORD_REQUIRE_LOWERCASE = True
    PASSWORD_REQUIRE_DIGIT = True
    PASSWORD_REQUIRE_SPECIAL = True

    # OAuth Google
    GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI", "http://localhost:5000/api/auth/google/callback")


class DevelopmentConfig(Config):
    """Configuration de développement."""

    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///colonie_dev.db"
    )
    # Disable rate limiting in development
    RATELIMIT_ENABLED = False


class StagingConfig(Config):
    """Configuration de staging."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # CORS plus restrictif
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")


class ProductionConfig(Config):
    """Configuration de production."""

    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")

    # Sécurité renforcée
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # CORS restrictif
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "").split(",")

    @classmethod
    def init_app(cls, app):
        """Validation configuration production."""
        assert os.environ.get("SECRET_KEY"), "SECRET_KEY must be set in production"
        assert os.environ.get("DATABASE_URL"), "DATABASE_URL must be set in production"


class TestingConfig(Config):
    """Configuration pour les tests."""

    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    RATELIMIT_ENABLED = False


config = {
    "development": DevelopmentConfig,
    "staging": StagingConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
