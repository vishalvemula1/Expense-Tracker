from app.models import User, UserCreate
from sqlmodel import Session
from app.services import AuthService
import pytest
from fastapi import HTTPException



class TestUserWhitespace:

    def test_duplicate_username_exists_whitespace(self, test_db: Session, test_user: User):
        new_user = UserCreate(
            username=" testuser ",
            email=" test@example2.com   ",
            salary=100,
            password="testpassword"
        )
        
        auth_service = AuthService(test_db)
        with pytest.raises(HTTPException) as exc_info:
            auth_service.create_user_with_defaults(new_user)

        assert exc_info.value.status_code == 409
        assert "Username already exists" in exc_info.value.detail

        
    def test_duplicate_email_exists_whitespace(self, test_db: Session, test_user: User):
        new_user = UserCreate(
            username="testuser2",
            email=" test@example.com ",
            salary=100,
            password="testpassword"
        )

        auth_service = AuthService(test_db)
        with pytest.raises(HTTPException) as exc_info:
            auth_service.create_user_with_defaults(new_user)

        assert exc_info.value.status_code == 409
        assert "Email already exists" in exc_info.value.detail

    

