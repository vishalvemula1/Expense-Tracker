import pytest
from sqlmodel import Session, select
from fastapi import HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.services.auth_service import AuthService
from app.models import User, UserCreate, Category
import jwt
from app.security import secret_key, algorithm


class TestCreateUserWithDefaults:
    """Tests for AuthService.create_user_with_defaults()"""

    def test_create_user_success(self, test_db: Session):
        """Happy path: Creating a user with default category"""
        auth_service = AuthService(test_db)
        user_create = UserCreate(
            username="newuser",
            email="new@example.com",
            salary=50000,
            password="securepass123"
        )

        user = auth_service.create_user_with_defaults(user_create)

        # Verify user was created correctly
        assert user.user_id is not None
        assert user.username == "newuser"
        assert user.email == "new@example.com"
        assert user.salary == 50000
        assert user.password_hash is not None
        assert user.password_hash != "securepass123"  # Password is hashed

        # Verify default category was created
        default_category = test_db.exec(
            select(Category).where(
                Category.user_id == user.user_id,
                Category.is_default
            )
        ).first()

        assert default_category is not None
        assert default_category.name == "Uncategorized"
        assert default_category.is_default

    def test_create_user_duplicate_username(self, test_db: Session, test_user: User):
        """409 Conflict: Cannot create user with duplicate username"""
        auth_service = AuthService(test_db)
        user_create = UserCreate(
            username="testuser",  # Same as test_user
            email="different@example.com",
            salary=50000,
            password="securepass123"
        )

        with pytest.raises(HTTPException) as exc_info:
            auth_service.create_user_with_defaults(user_create)

        assert exc_info.value.status_code == 409
        assert "Username already exists" in exc_info.value.detail

    def test_create_user_duplicate_email(self, test_db: Session, test_user: User):
        """409 Conflict: Cannot create user with duplicate email"""
        auth_service = AuthService(test_db)
        user_create = UserCreate(
            username="differentuser",
            email="test@example.com",  # Same as test_user
            salary=50000,
            password="securepass123"
        )

        with pytest.raises(HTTPException) as exc_info:
            auth_service.create_user_with_defaults(user_create)

        assert exc_info.value.status_code == 409
        assert "Email already exists" in exc_info.value.detail


class TestLogin:
    """Tests for AuthService.login()"""

    def test_login_success(self, test_db: Session, test_user: User):
        """Happy path: Login with correct credentials returns JWT token"""
        auth_service = AuthService(test_db)
        form_data = OAuth2PasswordRequestForm(
            username="testuser",
            password="testpassword",
            scope=""
        )

        token = auth_service.login(form_data)

        decoded = jwt.decode(token.access_token, secret_key, algorithms=[algorithm])
        assert decoded["sub"] == str(test_user.user_id)
        assert token.access_token is not None
        assert token.token_type == "bearer"

    def test_login_wrong_password(self, test_db: Session, test_user: User):
        """401 Unauthorized: Login with wrong password fails"""
        auth_service = AuthService(test_db)
        form_data = OAuth2PasswordRequestForm(
            username="testuser",
            password="wrongpassword",
            scope=""
        )

        with pytest.raises(HTTPException) as exc_info:
            auth_service.login(form_data)

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail

    def test_login_nonexistent_user(self, test_db: Session):
        """401 Unauthorized: Login with non-existent user fails"""
        auth_service = AuthService(test_db)
        form_data = OAuth2PasswordRequestForm(
            username="nonexistent",
            password="somepassword",
            scope=""
        )

        with pytest.raises(HTTPException) as exc_info:
            auth_service.login(form_data)

        assert exc_info.value.status_code == 401
        assert "Invalid username or password" in exc_info.value.detail

