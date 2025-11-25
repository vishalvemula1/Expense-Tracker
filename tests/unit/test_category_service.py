"""
CategoryService Unit Tests

Tests for category service internals:
- Default category protection (409 on update/delete)
- DB constraint for single default per user
- Partial update field preservation
- Uniqueness on update
- Cascade delete to expenses
- 404 for non-existent categories
"""
import pytest
from sqlmodel import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from datetime import date

from app.models import User, Category, CategoryCreate, CategoryUpdate, ExpenseCreate, Expense
from app.models.category import Color
from app.services import CategoryService, ExpenseService


class TestDefaultCategoryProtection:
    """Verify default category cannot be modified or deleted."""

    def test_cannot_update_default_category(self, test_db: Session, test_user: User, test_category: Category):
        """409: Cannot modify the default category"""
        svc = CategoryService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            svc.update(test_category.category_id, CategoryUpdate(name="Renamed"))  # type: ignore
        
        assert exc.value.status_code == 409
        assert "default" in exc.value.detail.lower()

    def test_cannot_delete_default_category(self, test_db: Session, test_user: User, test_category: Category):
        """409: Cannot delete the default category"""
        svc = CategoryService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            svc.delete(test_category.category_id)  # type: ignore
        
        assert exc.value.status_code == 409

    def test_db_prevents_multiple_default_categories(self, test_db: Session, test_user: User):
        """Database constraint prevents two default categories per user"""
        second_default = Category(
            name="second default",
            user_id=test_user.user_id,  # type: ignore
            is_default=True,
            date_of_entry=date.today()
        )
        test_db.add(second_default)
        
        with pytest.raises(IntegrityError):
            test_db.commit()
        
        test_db.rollback()


class TestPartialUpdate:
    """Verify partial updates preserve unspecified fields."""

    def test_partial_update_preserves_tag(
        self, test_db: Session, test_user: User, test_custom_category: Category
    ):
        """Updating name should not change tag"""
        original_tag = test_custom_category.tag
        svc = CategoryService(test_user, test_db)
        
        svc.update(test_custom_category.category_id, CategoryUpdate(name="New Name"))  # type: ignore
        
        test_db.refresh(test_custom_category)
        assert test_custom_category.tag == original_tag


class TestUniquenessOnUpdate:
    """Verify uniqueness constraints on update operations."""

    def test_update_to_existing_name_fails(
        self, test_db: Session, test_user: User, test_custom_category: Category
    ):
        """Cannot update category name to one that already exists (409)"""
        svc = CategoryService(test_user, test_db)
        svc.create(CategoryCreate(name="Existing Name", tag=Color.White))
        
        with pytest.raises(HTTPException) as exc:
            svc.update(test_custom_category.category_id, CategoryUpdate(name="Existing Name"))  # type: ignore
        
        assert exc.value.status_code == 409

    def test_update_to_own_name_succeeds(
        self, test_db: Session, test_user: User, test_custom_category: Category
    ):
        """Updating category name to same value should NOT trigger uniqueness error"""
        svc = CategoryService(test_user, test_db)
        original_name = test_custom_category.name
        
        svc.update(test_custom_category.category_id, CategoryUpdate(name=original_name))  # type: ignore
        
        test_db.refresh(test_custom_category)
        assert test_custom_category.name == original_name


class TestCascadeDelete:
    """Verify category deletion cascades to expenses."""

    def test_delete_cascades_to_expenses(self, test_db: Session, test_user: User):
        """Deleting category removes its expenses from DB"""
        cat_svc = CategoryService(test_user, test_db)
        exp_svc = ExpenseService(test_user, test_db)
        
        category = cat_svc.create(CategoryCreate(name="ToDelete", tag=Color.Red))
        exp1 = exp_svc.create(ExpenseCreate(name="Exp1", amount=50, category_id=category.category_id))
        exp2 = exp_svc.create(ExpenseCreate(name="Exp2", amount=75, category_id=category.category_id))
        
        exp1_id, exp2_id = exp1.expense_id, exp2.expense_id
        
        cat_svc.delete(category.category_id)  # type: ignore
        
        assert test_db.get(Expense, exp1_id) is None
        assert test_db.get(Expense, exp2_id) is None


class TestNotFound:
    """Verify 404 for non-existent resources."""

    def test_get_nonexistent_category_returns_404(self, test_db: Session, test_user: User):
        """Accessing category ID that doesn't exist returns 404"""
        svc = CategoryService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            svc.get(999999)
        
        assert exc.value.status_code == 404
