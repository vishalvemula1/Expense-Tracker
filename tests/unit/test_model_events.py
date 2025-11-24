import pytest
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from app.models import User, UserCreate, Category, CategoryUpdate
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.exceptions import AppExceptions
from datetime import date


class TestDefaultCategoryCreation:
    """Tests for automatic default category creation on user creation"""

    def test_create_user_creates_default_category(self, test_db: Session):
        """Creating a user automatically creates default 'Uncategorized' category"""
        user = User(
            username="eventuser",
            email="event@example.com",
            password_hash="hashed_secret",
            salary=1000
        )
        test_db.add(user)
        test_db.commit()
        test_db.refresh(user)

        # Check for default category
        statement = select(Category).where(
            Category.user_id == user.user_id,
            Category.is_default == True
        )
        category = test_db.exec(statement).first()

        assert category is not None
        assert category.name == "Uncategorized"
        assert category.is_default is True
        assert category.user_id == user.user_id


class TestDefaultCategoryProtection:
    """Tests for default category update/delete protection"""

    def test_prevent_default_category_update(self, test_db: Session, test_user: User):
        """409 Conflict: Cannot update default category"""
        statement = select(Category).where(
            Category.user_id == test_user.user_id,
            Category.is_default == True
        )
        default_category = test_db.exec(statement).first()
        assert default_category is not None

        category_service = CategoryService(test_user, test_db)
        update_request = CategoryUpdate(name="New Name")

        with pytest.raises(HTTPException) as exc_info:
            category_service.update(default_category.category_id, update_request)
        
        assert exc_info.value.status_code == 409
        assert "default category" in exc_info.value.detail.lower()

    def test_prevent_default_category_delete(self, test_db: Session, test_user: User):
        """409 Conflict: Cannot delete default category"""
        statement = select(Category).where(
            Category.user_id == test_user.user_id,
            Category.is_default == True
        )
        default_category = test_db.exec(statement).first()
        assert default_category is not None

        category_service = CategoryService(test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            category_service.delete(default_category.category_id)

        assert exc_info.value.status_code == 409
        assert "default category" in exc_info.value.detail.lower()


class TestDefaultCategoryConstraints:
    """Tests for database-level default category constraints"""

    def test_prevent_multiple_default_categories(self, test_db: Session, test_user: User):
        """Database constraint prevents multiple default categories per user"""
        # Verify the user already has one default category
        statement = select(Category).where(
            Category.user_id == test_user.user_id,
            Category.is_default == True
        )
        existing_default = test_db.exec(statement).first()
        assert existing_default is not None
        assert existing_default.name == "Uncategorized"
        
        # Attempt to create a second default category directly (bypassing service layer)
        second_default = Category(
            name="Another Default",
            user_id=test_user.user_id,
            is_default=True,
            date_of_entry=date.today()
        )
        test_db.add(second_default)
        
        # Should raise IntegrityError due to the partial unique index
        with pytest.raises(IntegrityError) as exc_info:
            test_db.commit()
        
        # Verify it's a unique constraint violation
        error_msg = str(exc_info.value).lower()
        assert "unique constraint" in error_msg or "unique" in error_msg
        
        # Rollback to clean up the session
        test_db.rollback()
