"""Tests for the health check endpoint."""
from fastapi.testclient import TestClient
from app.main import app


client = TestClient(app)


def test_health_check():
    """Test that /health returns 200 with correct fields."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "BusiAI"
    assert "version" in data


def test_root():
    """Test that / returns app info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == "BusiAI"
    assert "tagline" in data
