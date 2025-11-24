import pytest
from sqlmodel import Session
from fastapi import HTTPException
from app.services.expense_service import ExpenseService
from app.services.category_service import CategoryService
from app.services.auth_service import AuthService
from app.models import User, Category, Expense, ExpenseCreate, ExpenseUpdate, UserCreate, CategoryCreate
from datetime import date


class TestCreate:
    """Tests for ExpenseService.create()"""

    def test_create_expense_success(self, test_db: Session, test_user: User, test_category: Category):
        """Happy path: Create expense with valid category"""
        service = ExpenseService(test_user, test_db)
        expense_data = ExpenseCreate(
            name="Groceries",
            amount=50.0,
            category_id=test_category.category_id
        )

        expense = service.create(expense_data)

        assert expense.expense_id is not None
        assert expense.name == "Groceries"
        assert expense.amount == 50.0
        assert expense.user_id == test_user.user_id
        assert expense.category_id == test_category.category_id

    def test_create_expense_with_default_category(self, test_db: Session, test_user: User):
        """Creating expense with category_id=None uses default category"""
        service = ExpenseService(test_user, test_db)
        expense_data = ExpenseCreate(
            name="Misc",
            amount=25.0,
            category_id=None
        )

        expense = service.create(expense_data)

        # Should be assigned to default category
        category_service = CategoryService(test_user, test_db)
        default_cat = category_service._get_category(None)
        assert expense.category_id == default_cat.category_id

    def test_create_expense_invalid_category(self, test_db: Session, test_user: User):
        """404 Not Found: Cannot create expense with non-existent category"""
        service = ExpenseService(test_user, test_db)
        expense_data = ExpenseCreate(
            name="Test",
            amount=10.0,
            category_id=99999
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create(expense_data)

        assert exc_info.value.status_code == 404

    def test_create_expense_other_users_category(self, test_db: Session, test_user: User, other_user: User):
        """403 Forbidden: Cannot create expense using another user's category"""
        other_service = CategoryService(other_user, test_db)
        other_category = other_service.create(CategoryCreate(name="Other's Cat", tag="Red"))

        # test_user tries to use other_user's category
        service = ExpenseService(test_user, test_db)
        expense_data = ExpenseCreate(
            name="Test",
            amount=10.0,
            category_id=other_category.category_id
        )

        with pytest.raises(HTTPException) as exc_info:
            service.create(expense_data)

        assert exc_info.value.status_code == 403


class TestGet:
    """Tests for ExpenseService.get()"""

    def test_get_expense_success(self, test_db: Session, test_user: User, test_expense: Expense):
        """Retrieve expense by ID"""
        service = ExpenseService(test_user, test_db)

        expense = service.get(test_expense.expense_id)  # type: ignore

        assert expense.expense_id == test_expense.expense_id

    def test_get_expense_not_found(self, test_db: Session, test_user: User):
        """404 Not Found: Non-existent expense"""
        service = ExpenseService(test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.get(99999)

        assert exc_info.value.status_code == 404

    def test_get_expense_wrong_owner(self, test_db: Session, test_user: User, test_expense: Expense, other_user: User):
        """403 Forbidden: Cannot access another user's expense"""
        service = ExpenseService(other_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.get(test_expense.expense_id)  # type: ignore

        assert exc_info.value.status_code == 403


class TestUpdate:
    """Tests for ExpenseService.update()"""

    def test_update_expense_success(self, test_db: Session, test_user: User, test_expense: Expense, test_category: Category):
        """Happy path: Update expense fields"""
        service = ExpenseService(test_user, test_db)
        update_data = ExpenseUpdate(name="Updated Expense", amount=200.0, category_id=test_category.category_id)

        updated = service.update(test_expense.expense_id, update_data)  # type: ignore

        assert updated.name == "Updated Expense"
        assert updated.amount == 200.0
        assert updated.date_of_update == date.today()

    def test_update_expense_change_category(self, test_db: Session, test_user: User, test_expense: Expense):
        """Can change expense to a different owned category"""
        # Create new category
        cat_service = CategoryService(test_user, test_db)
        new_category = cat_service.create(CategoryCreate(name="New Cat", tag="Blue"))

        # Store original values to verify they don't change
        original_name = test_expense.name
        original_amount = test_expense.amount

        service = ExpenseService(test_user, test_db)
        # Only provide category_id - this is a TRUE partial update
        update_data = ExpenseUpdate(category_id=new_category.category_id)

        updated = service.update(test_expense.expense_id, update_data)  # type: ignore

        assert updated.category_id == new_category.category_id
        assert updated.name == original_name  # Verify unchanged
        assert updated.amount == original_amount  # Verify unchanged

    def test_update_expense_invalid_category(self, test_db: Session, test_user: User, test_expense: Expense):
        """404 Not Found: Cannot update expense to non-existent category"""
        service = ExpenseService(test_user, test_db)
        update_data = ExpenseUpdate(
            name=test_expense.name,
            amount=test_expense.amount,
            category_id=99999
        )

        with pytest.raises(HTTPException) as exc_info:
            service.update(test_expense.expense_id, update_data)  # type: ignore

        assert exc_info.value.status_code == 404

    def test_update_expense_other_users_category(self, test_db: Session, test_user: User, test_expense: Expense, other_user: User):
        """403 Forbidden: Cannot update expense to another user's category"""
        other_service = CategoryService(other_user, test_db)
        other_category = other_service.create(CategoryCreate(name="Other's Cat", tag="Red"))

        service = ExpenseService(test_user, test_db)
        update_data = ExpenseUpdate(
            name=test_expense.name,
            amount=test_expense.amount,
            category_id=other_category.category_id
        )

        with pytest.raises(HTTPException) as exc_info:
            service.update(test_expense.expense_id, update_data)  # type: ignore

        assert exc_info.value.status_code == 403

    def test_update_expense_wrong_owner(self, test_db: Session, test_user: User, test_expense: Expense, test_category: Category, other_user: User):
        """403 Forbidden: Cannot update another user's expense"""
        service = ExpenseService(other_user, test_db)
        update_data = ExpenseUpdate(name="Hacked", amount=9999.0, category_id=test_category.category_id)

        with pytest.raises(HTTPException) as exc_info:
            service.update(test_expense.expense_id, update_data)  # type: ignore

        assert exc_info.value.status_code == 403

    def test_update_expense_partial_amount_only(self, test_db: Session, test_user: User, test_custom_category: Category):
        """Partial update: only update amount, other fields unchanged including custom category"""
        # Create expense in CUSTOM category to catch bug where partial updates reset to default
        service = ExpenseService(test_user, test_db)
        expense = service.create(ExpenseCreate(
            name="Test Expense",
            amount=100.0,
            category_id=test_custom_category.category_id
        ))
        original_name = expense.name
        original_category = expense.category_id

        update_data = ExpenseUpdate(amount=999.99)

        updated = service.update(expense.expense_id, update_data)  # type: ignore

        assert updated.amount == 999.99
        assert updated.name == original_name
        assert updated.category_id == original_category  # Critical: preserves custom category

    def test_update_expense_not_found(self, test_db: Session, test_user: User):
        """404 Not Found: Cannot update non-existent expense"""
        service = ExpenseService(test_user, test_db)
        update_data = ExpenseUpdate(name="Ghost")

        with pytest.raises(HTTPException) as exc_info:
            service.update(99999, update_data)

        assert exc_info.value.status_code == 404


class TestDelete:
    """Tests for ExpenseService.delete()"""

    def test_delete_expense_success(self, test_db: Session, test_user: User, test_expense: Expense):
        """Happy path: Delete expense"""
        service = ExpenseService(test_user, test_db)
        expense_id = test_expense.expense_id

        service.delete(expense_id)  # type: ignore

        with pytest.raises(HTTPException) as exc_info:
            service.get(expense_id)  # type: ignore

        assert exc_info.value.status_code == 404

    def test_delete_expense_wrong_owner(self, test_db: Session, test_user: User, test_expense: Expense, other_user: User):
        """403 Forbidden: Cannot delete another user's expense"""
        service = ExpenseService(other_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.delete(test_expense.expense_id)  # type: ignore

        assert exc_info.value.status_code == 403

    def test_delete_expense_not_found(self, test_db: Session, test_user: User):
        """404 Not Found: Cannot delete non-existent expense"""
        service = ExpenseService(test_user, test_db)

        with pytest.raises(HTTPException) as exc_info:
            service.delete(99999)

        assert exc_info.value.status_code == 404


class TestList:
    """Tests for ExpenseService.list()"""

    def test_list_expenses_returns_only_own(self, test_db: Session, test_user: User, test_category: Category, other_user: User):
        """List should only return the current user's expenses"""
        service = ExpenseService(test_user, test_db)

        # Create expenses for test_user
        service.create(ExpenseCreate(name="Exp1", amount=10.0, category_id=test_category.category_id))
        service.create(ExpenseCreate(name="Exp2", amount=20.0, category_id=test_category.category_id))

        # Create expenses for other_user
        other_service = ExpenseService(other_user, test_db)
        other_cat_service = CategoryService(other_user, test_db)
        other_default = other_cat_service._get_category(None)
        other_service.create(ExpenseCreate(name="Other's Exp", amount=100.0, category_id=other_default.category_id))

        # List test_user's expenses
        expenses = service.list(limit=100, offset=0)

        assert len(expenses) == 2
        assert all(e.user_id == test_user.user_id for e in expenses)

    def test_list_expenses_pagination(self, test_db: Session, test_user: User, test_category: Category):
        """Pagination works correctly"""
        service = ExpenseService(test_user, test_db)

        # Create 5 expenses
        for i in range(5):
            service.create(ExpenseCreate(name=f"Exp{i}", amount=float(i * 10), category_id=test_category.category_id))

        page1 = service.list(limit=3, offset=0)
        page2 = service.list(limit=3, offset=3)

        assert len(page1) == 3
        assert len(page2) == 2

    def test_list_expenses_empty(self, test_db: Session, test_user: User):
        """List returns empty when user has no expenses"""
        service = ExpenseService(test_user, test_db)

        expenses = service.list(limit=100, offset=0)

        assert expenses == []
