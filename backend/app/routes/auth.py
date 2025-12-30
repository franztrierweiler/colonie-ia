"""
Authentication routes (placeholder for Phase 4)
"""
from flask import jsonify
from app.routes import api_bp


@api_bp.route("/auth/status", methods=["GET"])
def auth_status():
    """Auth module status (placeholder)."""
    return jsonify({
        "module": "auth",
        "status": "not_implemented",
        "endpoints": [
            "POST /api/auth/register",
            "POST /api/auth/login",
            "POST /api/auth/logout",
            "POST /api/auth/refresh",
            "POST /api/auth/forgot-password",
            "POST /api/auth/reset-password",
            "GET /api/auth/google",
            "GET /api/auth/google/callback",
        ]
    })
