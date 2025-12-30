"""
API Routes Blueprint
"""
from flask import Blueprint, jsonify

api_bp = Blueprint("api", __name__)


@api_bp.route("/health", methods=["GET"])
def health_check():
    """
    Vérification de l'état du service
    ---
    tags:
      - Système
    responses:
      200:
        description: Service opérationnel
        schema:
          type: object
          properties:
            status:
              type: string
              example: healthy
            service:
              type: string
              example: colonie-ia
    """
    return jsonify({"status": "healthy", "service": "colonie-ia"})


@api_bp.route("/version", methods=["GET"])
def version():
    """
    Version de l'API
    ---
    tags:
      - Système
    responses:
      200:
        description: Informations de version
        schema:
          type: object
          properties:
            version:
              type: string
              example: "0.1.0"
            name:
              type: string
              example: Colonie-IA API
    """
    return jsonify({
        "version": "0.1.0",
        "name": "Colonie-IA API",
    })


# Import and register route modules
from app.routes import auth  # noqa: F401, E402
from app.routes import users  # noqa: F401, E402
from app.routes import oauth  # noqa: F401, E402
from app.routes import games  # noqa: F401, E402
from app.routes import economy  # noqa: F401, E402
