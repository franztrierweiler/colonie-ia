"""
API Routes Blueprint
"""
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "colonie-ia"})


@api_bp.route("/version", methods=["GET"])
def version():
    """API version endpoint."""
    return jsonify({
        "version": "0.1.0",
        "name": "Colonie-IA API",
    })


# Import and register route modules
from app.routes import auth  # noqa: F401, E402
