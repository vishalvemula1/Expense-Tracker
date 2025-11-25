"""
AuthService Unit Tests

Tests for authentication internals not visible through HTTP responses:
- Password hashing (stored hash != plaintext)
- JWT token structure (payload contains user_id)
- Login error handling (401 for both wrong password and non-existent user)
"""
import pytest
from sqlmodel import Session
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
import jwt

from app.models import User, UserCreate
from app.services import AuthService
from app.security import secret_key, algorithm


class TestPasswordHashing:
    """Verify passwords are properly hashed, never stored as plaintext."""

    def test_password_is_hashed_not_plaintext(self, test_db: Session):
        """Password stored in DB is hashed, not plaintext"""
        auth = AuthService(test_db)
        user = auth.create_user_with_defaults(
            UserCreate(username="hashtest", email="hash@test.com", salary=0, password="mysecretpass")
        )
        
        assert user.password_hash is not None
        assert user.password_hash != "mysecretpass"
        assert len(user.password_hash) > 20  # bcrypt hash is ~60 chars


class TestJwtToken:
    """Verify JWT token structure and payload."""

    def test_jwt_payload_contains_user_id(self, test_db: Session, test_user: User):
        """JWT token payload contains correct user ID as 'sub' claim"""
        auth = AuthService(test_db)
        form = OAuth2PasswordRequestForm(username="testuser", password="testpassword", scope="")
        
        token = auth.login(form)
        decoded = jwt.decode(token.access_token, secret_key, algorithms=[algorithm])
        
        assert decoded["sub"] == str(test_user.user_id)
        assert "exp" in decoded  # Has expiration


class TestLoginErrors:
    """Verify login returns 401 for all auth failures (don't leak user existence)."""

    def test_wrong_password_returns_401(self, test_db: Session, test_user: User):
        """Wrong password returns 401, not 404"""
        auth = AuthService(test_db)
        form = OAuth2PasswordRequestForm(username="testuser", password="wrongpass", scope="")
        
        with pytest.raises(HTTPException) as exc:
            auth.login(form)
        
        assert exc.value.status_code == 401
        assert "Invalid username or password" in exc.value.detail

    def test_nonexistent_user_returns_401(self, test_db: Session):
        """Non-existent user returns 401, not 404 (same as wrong password)"""
        auth = AuthService(test_db)
        form = OAuth2PasswordRequestForm(username="nouser", password="anypass", scope="")
        
        with pytest.raises(HTTPException) as exc:
            auth.login(form)
        
        assert exc.value.status_code == 401
