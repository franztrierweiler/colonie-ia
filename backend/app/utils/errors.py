"""
Global error handlers
"""
from flask import jsonify


class APIError(Exception):
    """Base API Error."""

    def __init__(self, message: str, status_code: int = 400, payload: dict = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["error"] = self.message
        rv["status_code"] = self.status_code
        return rv


class ValidationError(APIError):
    """Validation error (400)."""

    def __init__(self, message: str, payload: dict = None):
        super().__init__(message, 400, payload)


class AuthenticationError(APIError):
    """Authentication error (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, 401)


class AuthorizationError(APIError):
    """Authorization error (403)."""

    def __init__(self, message: str = "Permission denied"):
        super().__init__(message, 403)


class NotFoundError(APIError):
    """Resource not found (404)."""

    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, 404)


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""

    def __init__(self, message: str = "Too many requests"):
        super().__init__(message, 429)


def register_error_handlers(app):
    """Register error handlers on Flask app."""

    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({"error": "Not found", "status_code": 404}), 404

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({"error": "Internal server error", "status_code": 500}), 500
