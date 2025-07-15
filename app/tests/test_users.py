"""
Tests for user endpoints.
"""
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.controllers.user_controller import user_controller
from app.schemas.user import UserCreate


def test_create_user(client: TestClient, db: Session) -> None:
    """Test user creation endpoint."""
    user_data = {
        "email": "test@example.com",
        "username": "testuser",
        "password": "password123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/users/", json=user_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert data["full_name"] == user_data["full_name"]
    assert "id" in data
    assert "password" not in data


def test_authenticate_user(client: TestClient, db: Session) -> None:
    """Test user authentication."""
    # Create a user first
    user_in = UserCreate(
        email="auth@example.com",
        username="authuser",
        password="password123",
        full_name="Auth User"
    )
    user_controller.create(db, obj_in=user_in)
    
    # Try to authenticate
    login_data = {
        "username": "authuser",
        "password": "password123"
    }
    
    response = client.post("/api/auth/token", data=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
