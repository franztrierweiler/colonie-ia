"""
Colonie-IA Backend Application
Flask application factory
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS

from app.config import config

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name: str = "development") -> Flask:
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # CORS configuration
    CORS(
        app,
        origins=app.config.get("CORS_ORIGINS", ["http://localhost:5173"]),
        supports_credentials=True,
    )

    # Register blueprints
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix="/api")

    # Register error handlers
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # Import models for migrations
    from app import models  # noqa: F401

    # Shell context
    @app.shell_context_processor
    def make_shell_context():
        from app.models import User, Game, GamePlayer
        return {"db": db, "User": User, "Game": Game, "GamePlayer": GamePlayer}

    return app
