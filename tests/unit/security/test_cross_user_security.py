"""
Cross-User Security Tests

Tests for multi-tenant security - users cannot access or use other users' resources.
Covers:
- Direct access attempts (get/update/delete) → 403
- Using other user's resources as FK (category_id) → 403
- List isolation (only see own data)
"""
import pytest
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models import (
    User, Category, CategoryCreate, CategoryUpdate,
    Expense, ExpenseCreate, ExpenseUpdate
)
from app.models.category_models import Color
from app.services import CategoryService, ExpenseService


# ============================================================================
# CATEGORY ACCESS
# ============================================================================

class TestCategoryAccess:

    @pytest.mark.parametrize("operation,args", [
        pytest.param(lambda svc, cat_id: svc.get(cat_id), (), id="get"),
        pytest.param(lambda svc, cat_id: svc.update(cat_id, CategoryUpdate(name="Hacked")), (), id="update"),
        pytest.param(lambda svc, cat_id: svc.delete(cat_id), (), id="delete"),
        pytest.param(lambda svc, cat_id: svc.get_expenses(cat_id), (), id="get_expenses"),
    ])
    def test_access_other_users_category_returns_403(
        self, test_db: Session, test_user: User, other_user: User, 
        test_custom_category: Category, operation, args
    ):
        svc = CategoryService(other_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            operation(svc, test_custom_category.category_id)
        
        assert exc.value.status_code == 403


# ============================================================================
# EXPENSE ACCESS
# ============================================================================

class TestExpenseAccess:

    @pytest.mark.parametrize("operation", [
        pytest.param(lambda svc, exp_id: svc.get(exp_id), id="get"),
        pytest.param(lambda svc, exp_id: svc.update(exp_id, ExpenseUpdate(amount=9999)), id="update"),
        pytest.param(lambda svc, exp_id: svc.delete(exp_id), id="delete"),
    ])
    def test_access_other_users_expense_returns_403(
        self, test_db: Session, test_user: User, other_user: User, test_expense: Expense, operation
    ):
        svc = ExpenseService(other_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            operation(svc, test_expense.expense_id)
        
        assert exc.value.status_code == 403


# ============================================================================
# CROSS-USER RESOURCE USAGE (FK references)
# ============================================================================

class TestCrossUserResourceUsage:

    def test_create_expense_with_other_users_category_fails(
        self, test_db: Session, test_user: User, other_user: User
    ):
        other_cat_svc = CategoryService(other_user, test_db)
        other_category = other_cat_svc.create(CategoryCreate(name="Other's Category", tag=Color.Blue))
        
        exp_svc = ExpenseService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            exp_svc.create(ExpenseCreate(
                name="Sneaky Expense",
                amount=100,
                category_id=other_category.category_id
            ))
        
        assert exc.value.status_code == 403

    def test_update_expense_to_other_users_category_fails(
        self, test_db: Session, test_user: User, other_user: User, test_expense: Expense
    ):
        other_cat_svc = CategoryService(other_user, test_db)
        other_category = other_cat_svc.create(CategoryCreate(name="Other's Category", tag=Color.Red))
        
        exp_svc = ExpenseService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            exp_svc.update(test_expense.expense_id, ExpenseUpdate(category_id=other_category.category_id))  # type: ignore
        
        assert exc.value.status_code == 403


# ============================================================================
# LIST ISOLATION
# ============================================================================

class TestListIsolation:

    def test_list_categories_excludes_other_users(
        self, test_db: Session, test_user: User, other_user: User
    ):
        cat_svc1 = CategoryService(test_user, test_db)
        cat_svc2 = CategoryService(other_user, test_db)
        
        cat_svc1.create(CategoryCreate(name="User1 Cat", tag=Color.Blue))
        cat_svc2.create(CategoryCreate(name="User2 Cat", tag=Color.Red))
        
        categories = cat_svc1.list(limit=100, offset=0)
        
        assert all(c.user_id == test_user.user_id for c in categories)
        assert not any(c.name == "user2 cat" for c in categories)

    def test_list_expenses_excludes_other_users(
        self, test_db: Session, test_user: User, other_user: User, test_category: Category
    ):
        exp_svc1 = ExpenseService(test_user, test_db)
        exp_svc2 = ExpenseService(other_user, test_db)
        
        other_default = test_db.exec(
            select(Category).where(
                Category.user_id == other_user.user_id,
                Category.is_default
            )
        ).first()
        
        exp_svc1.create(ExpenseCreate(name="User1 Expense", amount=100, category_id=test_category.category_id))
        exp_svc2.create(ExpenseCreate(name="User2 Expense", amount=200, category_id=other_default.category_id))  # type: ignore
        
        expenses = exp_svc1.list(limit=100, offset=0)
        
        assert all(e.user_id == test_user.user_id for e in expenses)
        assert not any(e.name == "User2 Expense" for e in expenses)
