"""
API endpoint tests
"""


def test_health_check(client):
    """Test health endpoint."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "colonie-ia"


def test_version(client):
    """Test version endpoint."""
    response = client.get("/api/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data
    assert data["name"] == "Colonie-IA API"


def test_auth_status(client):
    """Test auth status endpoint."""
    response = client.get("/api/auth/status")
    assert response.status_code == 200
    data = response.get_json()
    assert data["module"] == "auth"
