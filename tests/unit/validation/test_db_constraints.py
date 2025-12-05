"""
Database Constraint Tests

Tests for database-level uniqueness enforcement:
- Username uniqueness (case-insensitive, whitespace-normalized)
- Email uniqueness (case-insensitive, whitespace-normalized)
- Category name uniqueness per user

These test that normalization + DB constraints work together correctly.
"""
import pytest
from sqlmodel import Session
from fastapi import HTTPException

from app.models import UserCreate, CategoryCreate
from app.services import AuthService, CategoryService


class TestUserUniqueness:
    """
    Database uniqueness for username and email.
    Tests: exact match, whitespace-trimmed match, case-insensitive match.
    Expects: HTTPException 409 on duplicate.
    """

    @pytest.mark.parametrize("username", [
        pytest.param("testuser", id="exact"),
        pytest.param(" testuser ", id="whitespace"),
        pytest.param("TESTUSER", id="uppercase"),
    ])
    def test_duplicate_username_rejected(self, test_db: Session, test_user, username):
        """Duplicate username (exact, whitespace, case) -> 409"""
        with pytest.raises(HTTPException) as exc:
            AuthService(test_db).create_user_with_defaults(
                UserCreate(username=username, email="other@x.com", salary=0, password="validpass")
            )
        assert exc.value.status_code == 409

    @pytest.mark.parametrize("email", [
        pytest.param("test@example.com", id="exact"),
        pytest.param(" test@example.com ", id="whitespace"),
        pytest.param("TEST@EXAMPLE.COM", id="uppercase"),
    ])
    def test_duplicate_email_rejected(self, test_db: Session, test_user, email):
        """Duplicate email (exact, whitespace, case) -> 409"""
        with pytest.raises(HTTPException) as exc:
            AuthService(test_db).create_user_with_defaults(
                UserCreate(username="newuser", email=email, salary=0, password="validpass")
            )
        assert exc.value.status_code == 409


class TestCategoryUniqueness:
    """
    Database uniqueness for category name per user (name + user_id).
    Tests: same user duplicate, whitespace, case; different user same name.
    Expects: 409 for same user duplicates, success for different users.
    
    NOTE: We create categories through CategoryService (not raw DB inserts)
    to ensure names are normalized via Pydantic validators before storage.
    """

    @pytest.mark.parametrize("duplicate_name", [
        pytest.param("groceries", id="exact"),
        pytest.param("GROCERIES", id="uppercase"),
        pytest.param("  Groceries  ", id="whitespace"),
    ])
    def test_duplicate_name_same_user_rejected(self, test_db: Session, test_user, duplicate_name):
        """Duplicate category name (exact, case, whitespace) -> 409"""
        svc = CategoryService(test_user, test_db)
        svc.create(CategoryCreate(name="Groceries"))
        
        with pytest.raises(HTTPException) as exc:
            svc.create(CategoryCreate(name=duplicate_name))
        assert exc.value.status_code == 409

    def test_same_name_different_users_accepted(self, test_db: Session, test_user, other_user):
        """User1 has 'shared' -> User2 can also have 'shared'"""
        svc1 = CategoryService(test_user, test_db)
        svc1.create(CategoryCreate(name="Shared"))

        svc2 = CategoryService(other_user, test_db)
        cat2 = svc2.create(CategoryCreate(name="Shared"))
        
        assert cat2.name == "shared"  # lowercased
        assert cat2.user_id == other_user.user_id
