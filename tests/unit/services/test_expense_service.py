"""
ExpenseService Unit Tests

Tests for expense service internals:
- NULL category defaults to user's default category
- Partial update field preservation
- Date tracking (date_of_entry, date_of_update)
- 404 for non-existent expenses/categories
"""
import pytest
from sqlmodel import Session
from fastapi import HTTPException
from datetime import date

from app.models import User, Category, Expense, ExpenseCreate, ExpenseUpdate
from app.services import ExpenseService


class TestNullCategoryHandling:
    """Verify NULL category_id defaults to user's default category."""

    def test_null_category_uses_default(
        self, test_db: Session, test_user: User, test_category: Category
    ):
        """Creating expense with category_id=None uses user's default category"""
        svc = ExpenseService(test_user, test_db)
        
        expense = svc.create(ExpenseCreate(name="No Category", amount=50, category_id=None))
        
        assert expense.category_id == test_category.category_id
        assert test_category.is_default is True


class TestPartialUpdate:
    """Verify partial updates preserve unspecified fields."""

    def test_partial_update_preserves_category(
        self, test_db: Session, test_user: User, test_custom_category: Category
    ):
        """
        BUG HUNTER: Partial update should NOT reset category to default.
        This catches a common bug where PATCH semantics aren't implemented correctly.
        """
        svc = ExpenseService(test_user, test_db)
        
        expense = svc.create(ExpenseCreate(
            name="In Custom Category",
            amount=100,
            category_id=test_custom_category.category_id
        ))
        
        svc.update(expense.expense_id, ExpenseUpdate(amount=999))  # type: ignore
        
        test_db.refresh(expense)
        assert expense.category_id == test_custom_category.category_id, \
            "BUG: Partial update reset category to default!"

    def test_partial_update_preserves_name(
        self, test_db: Session, test_user: User, test_category: Category
    ):
        """Updating amount should not change name"""
        svc = ExpenseService(test_user, test_db)
        expense = svc.create(ExpenseCreate(
            name="Original Name",
            amount=100,
            category_id=test_category.category_id
        ))
        
        svc.update(expense.expense_id, ExpenseUpdate(amount=200))  # type: ignore
        
        test_db.refresh(expense)
        assert expense.name == "Original Name"
        assert expense.amount == 200


class TestDateTracking:
    """Verify date fields are set correctly."""

    def test_date_of_entry_set_on_create(
        self, test_db: Session, test_user: User, test_category: Category
    ):
        """Expense date_of_entry is automatically set to today"""
        svc = ExpenseService(test_user, test_db)
        
        expense = svc.create(ExpenseCreate(name="Dated", amount=100, category_id=test_category.category_id))
        
        assert expense.date_of_entry == date.today()

    def test_date_of_update_set_on_update(
        self, test_db: Session, test_user: User, test_expense: Expense
    ):
        """Expense date_of_update is set when expense is modified"""
        svc = ExpenseService(test_user, test_db)
        
        assert test_expense.date_of_update is None
        
        svc.update(test_expense.expense_id, ExpenseUpdate(amount=999))  # type: ignore
        
        test_db.refresh(test_expense)
        assert test_expense.date_of_update == date.today()


class TestNotFound:
    """Verify 404 for non-existent resources."""

    def test_get_nonexistent_expense_returns_404(self, test_db: Session, test_user: User):
        """Accessing expense ID that doesn't exist returns 404"""
        svc = ExpenseService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            svc.get(999999)
        
        assert exc.value.status_code == 404

    def test_create_with_nonexistent_category_returns_404(self, test_db: Session, test_user: User):
        """Creating expense with non-existent category_id returns 404"""
        svc = ExpenseService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            svc.create(ExpenseCreate(name="Bad Cat", amount=100, category_id=999999))
        
        assert exc.value.status_code == 404
