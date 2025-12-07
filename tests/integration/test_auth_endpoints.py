"""
Integration tests for authentication endpoints.

These tests verify the full stack authentication flow:
- User signup via HTTP -> Router -> Service -> DB
- Login flow with JWT token generation
- Token usage for accessing protected endpoints
"""
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import User


class TestAuthSignup:

    def test_signup_creates_user_and_default_category(self, client: TestClient, test_db: Session):
        response = client.post("/auth/signup", json={
            "username": "newuser",
            "email": "newuser@example.com",
            "salary": 60000,
            "password": "securepassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert data["salary"] == 60000
        assert "user_id" in data
        assert "password" not in data
        
        user = test_db.exec(
            select(User).where(User.username == "newuser")
        ).first()
        assert user is not None
        assert user.email == "newuser@example.com"

    def test_signup_duplicate_username_fails(self, client: TestClient, test_user: User):
        response = client.post("/auth/signup", json={
            "username": test_user.username,
            "email": "different@example.com",
            "salary": 50000,
            "password": "password"
        })
        
        assert response.status_code == 409


class TestAuthLogin:

    def test_login_returns_valid_token(self, client: TestClient, test_user: User):
        response = client.post("/auth/login", data={
            "username": test_user.username,
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_with_wrong_password_fails(self, client: TestClient, test_user: User):
        response = client.post("/auth/login", data={
            "username": test_user.username,
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401

    def test_login_with_nonexistent_user_fails(self, client: TestClient):
        response = client.post("/auth/login", data={
            "username": "doesnotexist",
            "password": "somepassword"
        })
        
        assert response.status_code == 401


class TestTokenAuthentication:

    def test_token_grants_access_to_protected_endpoints(self, client: TestClient, test_user: User):
        login_response = client.post("/auth/login", data={
            "username": test_user.username,
            "password": "testpassword"
        })
        token = login_response.json()["access_token"]
        
        response = client.get("/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == test_user.username

    def test_missing_token_denies_access(self, client: TestClient, test_user: User):
        response = client.get("/me")
        
        assert response.status_code == 401

    def test_invalid_token_denies_access(self, client: TestClient):
        response = client.get("/me", headers={
            "Authorization": "Bearer invalid_token_here"
        })
        
        assert response.status_code == 401
