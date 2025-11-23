import pytest
from sqlmodel import Session, select
from fastapi import HTTPException
from app.services.user_service import UserService
from app.models import User, UserUpdate, Category, Expense


class TestGetUser:
    """Tests for UserService.get_user() static method"""

    def test_get_user_success(self, test_db: Session, test_user: User):
        """Retrieve user by ID"""
        user = UserService.get_user(test_user.user_id, test_db)  # type: ignore

        assert user.user_id == test_user.user_id
        assert user.username == test_user.username

    def test_get_user_not_found(self, test_db: Session):
        """404 Not Found: Non-existent user ID"""
        with pytest.raises(HTTPException) as exc_info:
            UserService.get_user(99999, test_db)

        assert exc_info.value.status_code == 404


class TestGet:
    """Tests for UserService.get()"""

    def test_get_current_user_success(self, test_db: Session, test_user: User):
        """Returns the authenticated user's profile"""
        service = UserService(test_user, test_db)

        user = service.get()

        assert user.user_id == test_user.user_id
        assert user.username == test_user.username
        assert user.email == test_user.email


class TestUpdate:
    """Tests for UserService.update()"""

    def test_update_user_partial_fields(self, test_db: Session, test_user: User):
        """Partial update: Only specified fields change"""
        service = UserService(test_user, test_db)
        update_data = UserUpdate(username="updateduser", salary=75000)

        updated = service.update(update_data)

        assert updated.username == "updateduser"
        assert updated.salary == 75000
        assert updated.email == "test@example.com"  # Unchanged

    def test_update_user_password_is_hashed(self, test_db: Session, test_user: User):
        """Password updates are hashed"""
        service = UserService(test_user, test_db)
        old_hash = test_user.password_hash
        update_data = UserUpdate(password="newpassword123")

        updated = service.update(update_data)

        assert updated.password_hash != old_hash
        assert updated.password_hash != "newpassword123"

    def test_update_user_duplicate_username(self, test_db: Session, test_user: User, other_user: User):
        """409 Conflict: Cannot update to existing username"""
        service = UserService(test_user, test_db)
        update_data = UserUpdate(username="otheruser")

        with pytest.raises(HTTPException) as exc_info:
            service.update(update_data)

        assert exc_info.value.status_code == 409
        assert "Username already exists" in exc_info.value.detail

    def test_update_user_duplicate_email(self, test_db: Session, test_user: User, other_user: User):
        """409 Conflict: Cannot update to existing email"""
        service = UserService(test_user, test_db)
        update_data = UserUpdate(email="other@example.com")

        with pytest.raises(HTTPException) as exc_info:
            service.update(update_data)

        assert exc_info.value.status_code == 409
        assert "Email already exists" in exc_info.value.detail

    def test_update_user_empty_update(self, test_db: Session, test_user: User):
        """Empty update makes no changes"""
        service = UserService(test_user, test_db)
        original_username = test_user.username
        update_data = UserUpdate()

        updated = service.update(update_data)

        assert updated.username == original_username


class TestDelete:
    """Tests for UserService.delete()"""

    def test_delete_user_success(self, test_db: Session, test_user: User):
        """User deletion removes from database"""
        user_id = test_user.user_id
        service = UserService(test_user, test_db)

        service.delete()

        # Verify user is gone
        with pytest.raises(HTTPException) as exc_info:
            UserService.get_user(user_id, test_db)  # type: ignore

        assert exc_info.value.status_code == 404

    def test_delete_user_cascades_to_categories_and_expenses(self, test_db: Session, test_user: User):
        """User deletion cascades to categories and expenses"""
        from app.services.category_service import CategoryService
        from app.services.expense_service import ExpenseService
        from app.models import CategoryCreate, ExpenseCreate
        
        # Create a custom category
        cat_service = CategoryService(test_user, test_db)
        category = cat_service.create(CategoryCreate(name="Test Cat", tag="Blue"))
        category_id = category.category_id
        
        # Create an expense
        exp_service = ExpenseService(test_user, test_db)
        expense = exp_service.create(ExpenseCreate(
            name="Test Expense",
            amount=50.0,
            category_id=category_id
        ))
        expense_id = expense.expense_id
        
        user_id = test_user.user_id
        
        # Delete the user
        service = UserService(test_user, test_db)
        service.delete()
        
        # Verify user is gone
        with pytest.raises(HTTPException) as exc_info:
            UserService.get_user(user_id, test_db)  # type: ignore
        assert exc_info.value.status_code == 404
        
        # Verify categories are cascade deleted
        categories = test_db.exec(select(Category).where(Category.user_id == user_id)).all()
        assert len(categories) == 0
        
        # Verify expenses are cascade deleted
        expenses = test_db.exec(select(Expense).where(Expense.user_id == user_id)).all()
        assert len(expenses) == 0
