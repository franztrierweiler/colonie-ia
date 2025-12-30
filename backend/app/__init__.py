"""
Colonie-IA Backend Application
Flask application factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flasgger import Swagger

from app.config import config

db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO()
limiter = Limiter(key_func=get_remote_address)
swagger = Swagger()


def create_app(config_name: str = "development") -> Flask:
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Only enable rate limiter if configured
    if app.config.get("RATELIMIT_ENABLED", True):
        limiter.init_app(app)

    # CORS configuration
    cors_origins = app.config.get("CORS_ORIGINS", ["http://localhost:5173"])
    CORS(
        app,
        origins=cors_origins,
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        expose_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # SocketIO configuration
    socketio.init_app(
        app,
        cors_allowed_origins=cors_origins,
        async_mode="threading",
    )

    # Swagger/OpenAPI configuration
    app.config["SWAGGER"] = {
        "title": "Colonie-IA API",
        "description": "API pour le jeu de stratégie galactique Colonie-IA",
        "version": "1.0.0",
        "termsOfService": "",
        "uiversion": 3,
        "specs_route": "/api/docs/",
        "headers": [],
        "specs": [
            {
                "endpoint": "apispec",
                "route": "/api/docs/apispec.json",
            }
        ],
    }
    swagger.init_app(app)

    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Security headers
    @app.after_request
    def add_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not app.debug:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

    # Register WebSocket events
    from app import websocket  # noqa: F401

    # Import models for migrations
    from app import models  # noqa: F401

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Game, GamePlayer
        return {"db": db, "User": User, "Game": Game, "GamePlayer": GamePlayer}

    return app
