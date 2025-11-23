import pytest
from sqlmodel import Session
from fastapi import HTTPException
from app.services.category_service import CategoryService
from app.services.auth_service import AuthService
from app.models import User, Category, CategoryCreate, CategoryUpdate, UserCreate, Expense


class TestCreate:
    """Tests for CategoryService.create()"""

    def test_create_category_success(self, test_db: Session, test_user: User):
        """Happy path: Create category with unique name"""
        service = CategoryService(test_user, test_db)
        category_data = CategoryCreate(
            name="Food",
            description="Food expenses",
            tag="Blue"
        )

        category = service.create(category_data)

        assert category.category_id is not None
        assert category.name == "Food"
        assert category.user_id == test_user.user_id
        assert category.is_default == False

    def test_create_category_duplicate_name(self, test_db: Session, test_user: User):
        """409 Conflict: Category names must be unique per user"""
        service = CategoryService(test_user, test_db)
        category_data = CategoryCreate(
            name="Food",
            tag="Blue"
        )

        service.create(category_data)

        # Try to create another with same name
        with pytest.raises(HTTPException) as exc_info:
            service.create(category_data)

        assert exc_info.value.status_code == 409

    def test_create_category_same_name_different_users(self, test_db: Session, test_user: User, other_user: User):
        """Different users can have categories with the same name"""
        # Create category for test_user
        service1 = CategoryService(test_user, test_db)
        service1.create(CategoryCreate(name="Food", tag="Blue"))

        # Other user can also have "Food" category
        service2 = CategoryService(other_user, test_db)
        category = service2.create(CategoryCreate(name="Food", tag="Red"))

        assert category.name == "Food"
        assert category.user_id == other_user.user_id


class TestGet:
    """Tests for CategoryService.get()"""

    def test_get_category_success(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Retrieve category by ID"""
        service = CategoryService(test_user, test_db)

        category = service.get(test_custom_category.category_id)  # type: ignore

        assert category.category_id == test_custom_category.category_id

    def test_get_category_not_found(self, test_db: Session, test_user: User):
        """404 Not Found: Non-existent category"""
        service = CategoryService(test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.get(99999)

        assert exc_info.value.status_code == 404

    def test_get_category_wrong_owner(self, test_db: Session, test_user: User, test_custom_category: Category, other_user: User):
        """403 Forbidden: Cannot access another user's category"""
        # Other user tries to access test_user's category
        service = CategoryService(other_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.get(test_custom_category.category_id)  # type: ignore

        assert exc_info.value.status_code == 403


class TestUpdate:
    """Tests for CategoryService.update()"""

    def test_update_category_success(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Happy path: Update category fields"""
        service = CategoryService(test_user, test_db)
        update_data = CategoryUpdate(name="Updated Name", tag="Red")

        updated = service.update(test_custom_category.category_id, update_data)  # type: ignore

        assert updated.name == "Updated Name"
        assert updated.tag == "Red"

    def test_update_default_category_conflict(self, test_db: Session, test_user: User, test_category: Category):
        """409 Conflict: Cannot update the default category"""
        service = CategoryService(test_user, test_db)
        update_data = CategoryUpdate(name="New Name")

        with pytest.raises(HTTPException) as exc_info:
            service.update(test_category.category_id, update_data)  # type: ignore

        assert exc_info.value.status_code == 409

    def test_update_category_duplicate_name(self, test_db: Session, test_user: User, test_custom_category: Category):
        """409 Conflict: Cannot update to a name that already exists for this user"""
        service = CategoryService(test_user, test_db)

        # Create another category
        other_cat = service.create(CategoryCreate(name="Other", tag="White"))

        # Try to rename test_custom_category to "Other"
        update_data = CategoryUpdate(name="Other")

        with pytest.raises(HTTPException) as exc_info:
            service.update(test_custom_category.category_id, update_data)  # type: ignore

        assert exc_info.value.status_code == 409

    def test_update_category_wrong_owner(self, test_db: Session, test_user: User, test_custom_category: Category, other_user: User):
        """403 Forbidden: Cannot update another user's category"""
        service = CategoryService(other_user, test_db)
        update_data = CategoryUpdate(name="Hacked")

        with pytest.raises(HTTPException) as exc_info:
            service.update(test_custom_category.category_id, update_data)  # type: ignore

        assert exc_info.value.status_code == 403

    def test_update_category_partial_name_only(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Partial update: only update name, other fields unchanged"""
        service = CategoryService(test_user, test_db)
        original_tag = test_custom_category.tag

        update_data = CategoryUpdate(name="Partially Updated")

        updated = service.update(test_custom_category.category_id, update_data)  # type: ignore

        assert updated.name == "Partially Updated"
        assert updated.tag == original_tag

    def test_update_category_partial_tag_only(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Partial update: only update tag, other fields unchanged"""
        service = CategoryService(test_user, test_db)
        original_name = test_custom_category.name

        update_data = CategoryUpdate(tag="Black")

        updated = service.update(test_custom_category.category_id, update_data)  # type: ignore

        assert updated.tag == "Black"
        assert updated.name == original_name

    def test_update_category_not_found(self, test_db: Session, test_user: User):
        """404 Not Found: Cannot update non-existent category"""
        service = CategoryService(test_user, test_db)
        update_data = CategoryUpdate(name="Ghost")

        with pytest.raises(HTTPException) as exc_info:
            service.update(99999, update_data)

        assert exc_info.value.status_code == 404


class TestDelete:
    """Tests for CategoryService.delete()"""

    def test_delete_category_success(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Happy path: Delete category"""
        service = CategoryService(test_user, test_db)
        category_id = test_custom_category.category_id

        service.delete(category_id)  # type: ignore

        # Verify deleted
        with pytest.raises(HTTPException) as exc_info:
            service.get(category_id)  # type: ignore

        assert exc_info.value.status_code == 404

    def test_delete_default_category_conflict(self, test_db: Session, test_user: User, test_category: Category):
        """409 Conflict: Cannot delete the default category"""
        service = CategoryService(test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.delete(test_category.category_id)  # type: ignore

        assert exc_info.value.status_code == 409

    def test_delete_category_wrong_owner(self, test_db: Session, test_user: User, test_custom_category: Category, other_user: User):
        """403 Forbidden: Cannot delete another user's category"""
        service = CategoryService(other_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.delete(test_custom_category.category_id)  # type: ignore

        assert exc_info.value.status_code == 403

    def test_delete_category_not_found(self, test_db: Session, test_user: User):
        """404 Not Found: Cannot delete non-existent category"""
        service = CategoryService(test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.delete(99999)

        assert exc_info.value.status_code == 404

    def test_delete_category_cascades_to_expenses(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Deleting a category should cascade delete its expenses"""
        from app.services.expense_service import ExpenseService
        from app.models import ExpenseCreate
        
        # Create an expense in the custom category
        expense_service = ExpenseService(test_user, test_db)
        expense = expense_service.create(ExpenseCreate(
            name="Test Expense",
            amount=100.0,
            category_id=test_custom_category.category_id
        ))
        expense_id = expense.expense_id
        
        # Delete the category
        category_service = CategoryService(test_user, test_db)
        category_service.delete(test_custom_category.category_id)  # type: ignore
        
        # Verify expense was cascade deleted
        with pytest.raises(HTTPException) as exc_info:
            expense_service.get(expense_id)  # type: ignore
        
        assert exc_info.value.status_code == 404


class TestList:
    """Tests for CategoryService.list()"""

    def test_list_categories_returns_only_own(self, test_db: Session, test_user: User, other_user: User):
        """List should only return the current user's categories"""
        service = CategoryService(test_user, test_db)

        # Create some categories
        service.create(CategoryCreate(name="Food", tag="Blue"))
        service.create(CategoryCreate(name="Travel", tag="Red"))

        # Other user creates a category
        other_service = CategoryService(other_user, test_db)
        other_service.create(CategoryCreate(name="Other's Cat", tag="Black"))

        # List test_user's categories
        categories = service.list(limit=100, offset=0)

        # Should have default + 2 created = 3
        assert len(categories) == 3
        assert all(c.user_id == test_user.user_id for c in categories)

    def test_list_categories_pagination(self, test_db: Session, test_user: User):
        """Pagination works correctly"""
        service = CategoryService(test_user, test_db)

        # Create 5 categories
        for i in range(5):
            service.create(CategoryCreate(name=f"Cat{i}", tag="Blue"))

        # Total: 1 default + 5 = 6
        page1 = service.list(limit=3, offset=0)
        page2 = service.list(limit=3, offset=3)

        assert len(page1) == 3
        assert len(page2) == 3


class TestGetExpenses:
    """Tests for CategoryService.get_expenses()"""

    def test_get_expenses_success(self, test_db: Session, test_user: User, test_category: Category, test_expense: Expense):
        """Get all expenses for a category"""
        service = CategoryService(test_user, test_db)

        expenses = service.get_expenses(test_category.category_id)  # type: ignore

        assert len(expenses) == 1
        assert expenses[0].expense_id == test_expense.expense_id

    def test_get_expenses_empty_category(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Empty category returns empty list"""
        service = CategoryService(test_user, test_db)

        expenses = service.get_expenses(test_custom_category.category_id)  # type: ignore

        assert expenses == []

    def test_get_expenses_wrong_owner(self, test_db: Session, test_user: User, test_category: Category, other_user: User):
        """403 Forbidden: Cannot get expenses from another user's category"""
        service = CategoryService(other_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.get_expenses(test_category.category_id)  # type: ignore

        assert exc_info.value.status_code == 403
