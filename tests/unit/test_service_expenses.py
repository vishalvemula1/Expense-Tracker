import pytest
from sqlmodel import Session
from fastapi import HTTPException
from app.services.expense_service import ExpenseService
from app.services.category_service import CategoryService
from app.services.auth_service import AuthService
from app.models import User, Category, Expense, ExpenseCreate, ExpenseUpdate, UserCreate, CategoryCreate
from datetime import date


# ====================================================================
# create: Creates expense with category validation
# ====================================================================

def test_create_expense_success(test_db: Session, test_user: User, test_category: Category):
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


def test_create_expense_with_default_category(test_db: Session, test_user: User):
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


def test_create_expense_invalid_category(test_db: Session, test_user: User):
    """Cannot create expense with non-existent category"""
    service = ExpenseService(test_user, test_db)
    expense_data = ExpenseCreate(
        name="Test",
        amount=10.0,
        category_id=99999
    )

    with pytest.raises(HTTPException) as exc_info:
        service.create(expense_data)

    assert exc_info.value.status_code == 404


def test_create_expense_other_users_category(test_db: Session, test_user: User):
    """Cannot create expense using another user's category"""
    # Create another user with a category
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))
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


# ====================================================================
# get: Retrieves expense with ownership check
# ====================================================================

def test_get_expense_success(test_db: Session, test_user: User, test_expense: Expense):
    service = ExpenseService(test_user, test_db)

    expense = service.get(test_expense.expense_id)  # type: ignore

    assert expense.expense_id == test_expense.expense_id


def test_get_expense_not_found(test_db: Session, test_user: User):
    service = ExpenseService(test_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get(99999)

    assert exc_info.value.status_code == 404


def test_get_expense_wrong_owner(test_db: Session, test_user: User, test_expense: Expense):
    """Cannot access another user's expense"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = ExpenseService(other_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get(test_expense.expense_id)  # type: ignore

    assert exc_info.value.status_code == 403


# ====================================================================
# update: Updates expense with category validation
# ====================================================================

def test_update_expense_success(test_db: Session, test_user: User, test_expense: Expense, test_category: Category):
    service = ExpenseService(test_user, test_db)
    update_data = ExpenseUpdate(name="Updated Expense", amount=200.0, category_id=test_category.category_id)

    updated = service.update(test_expense.expense_id, update_data)  # type: ignore

    assert updated.name == "Updated Expense"
    assert updated.amount == 200.0
    assert updated.date_of_update == date.today()


def test_update_expense_change_category(test_db: Session, test_user: User, test_expense: Expense):
    """Can change expense to a different owned category"""
    # Create new category
    cat_service = CategoryService(test_user, test_db)
    new_category = cat_service.create(CategoryCreate(name="New Cat", tag="Blue"))

    service = ExpenseService(test_user, test_db)
    update_data = ExpenseUpdate(
        name=test_expense.name,
        amount=test_expense.amount,
        category_id=new_category.category_id
    )

    updated = service.update(test_expense.expense_id, update_data)  # type: ignore

    assert updated.category_id == new_category.category_id


def test_update_expense_invalid_category(test_db: Session, test_user: User, test_expense: Expense):
    """Cannot update expense to non-existent category"""
    service = ExpenseService(test_user, test_db)
    update_data = ExpenseUpdate(
        name=test_expense.name,
        amount=test_expense.amount,
        category_id=99999
    )

    with pytest.raises(HTTPException) as exc_info:
        service.update(test_expense.expense_id, update_data)  # type: ignore

    assert exc_info.value.status_code == 404


def test_update_expense_other_users_category(test_db: Session, test_user: User, test_expense: Expense):
    """Cannot update expense to another user's category"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))
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


def test_update_expense_wrong_owner(test_db: Session, test_user: User, test_expense: Expense, test_category: Category):
    """Cannot update another user's expense"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = ExpenseService(other_user, test_db)
    update_data = ExpenseUpdate(name="Hacked", amount=9999.0, category_id=test_category.category_id)

    with pytest.raises(HTTPException) as exc_info:
        service.update(test_expense.expense_id, update_data)  # type: ignore

    assert exc_info.value.status_code == 403


def test_update_expense_partial_name_only(test_db: Session, test_user: User, test_expense: Expense):
    """Partial update: only update name, other fields unchanged"""
    service = ExpenseService(test_user, test_db)
    original_amount = test_expense.amount
    original_category = test_expense.category_id

    update_data = ExpenseUpdate(name="Only Name Changed")

    updated = service.update(test_expense.expense_id, update_data)  # type: ignore

    assert updated.name == "Only Name Changed"
    assert updated.amount == original_amount
    assert updated.category_id == original_category


def test_update_expense_partial_amount_only(test_db: Session, test_user: User, test_expense: Expense):
    """Partial update: only update amount, other fields unchanged"""
    service = ExpenseService(test_user, test_db)
    original_name = test_expense.name

    update_data = ExpenseUpdate(amount=999.99)

    updated = service.update(test_expense.expense_id, update_data)  # type: ignore

    assert updated.amount == 999.99
    assert updated.name == original_name


def test_update_expense_not_found(test_db: Session, test_user: User):
    """Cannot update non-existent expense"""
    service = ExpenseService(test_user, test_db)
    update_data = ExpenseUpdate(name="Ghost")

    with pytest.raises(HTTPException) as exc_info:
        service.update(99999, update_data)

    assert exc_info.value.status_code == 404


# ====================================================================
# delete: Deletes expense with ownership check
# ====================================================================

def test_delete_expense_success(test_db: Session, test_user: User, test_expense: Expense):
    service = ExpenseService(test_user, test_db)
    expense_id = test_expense.expense_id

    service.delete(expense_id)  # type: ignore

    with pytest.raises(HTTPException) as exc_info:
        service.get(expense_id)  # type: ignore

    assert exc_info.value.status_code == 404


def test_delete_expense_wrong_owner(test_db: Session, test_user: User, test_expense: Expense):
    """Cannot delete another user's expense"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = ExpenseService(other_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(test_expense.expense_id)  # type: ignore

    assert exc_info.value.status_code == 403


def test_delete_expense_not_found(test_db: Session, test_user: User):
    """Cannot delete non-existent expense"""
    service = ExpenseService(test_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(99999)

    assert exc_info.value.status_code == 404


# ====================================================================
# list: Returns user's expenses with pagination
# ====================================================================

def test_list_expenses_returns_only_own(test_db: Session, test_user: User, test_category: Category):
    """List should only return the current user's expenses"""
    service = ExpenseService(test_user, test_db)

    # Create expenses for test_user
    service.create(ExpenseCreate(name="Exp1", amount=10.0, category_id=test_category.category_id))
    service.create(ExpenseCreate(name="Exp2", amount=20.0, category_id=test_category.category_id))

    # Create another user with expenses
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))
    other_service = ExpenseService(other_user, test_db)
    other_cat_service = CategoryService(other_user, test_db)
    other_default = other_cat_service._get_category(None)
    other_service.create(ExpenseCreate(name="Other's Exp", amount=100.0, category_id=other_default.category_id))

    # List test_user's expenses
    expenses = service.list(limit=100, offset=0)

    assert len(expenses) == 2
    assert all(e.user_id == test_user.user_id for e in expenses)


def test_list_expenses_pagination(test_db: Session, test_user: User, test_category: Category):
    service = ExpenseService(test_user, test_db)

    # Create 5 expenses
    for i in range(5):
        service.create(ExpenseCreate(name=f"Exp{i}", amount=float(i * 10), category_id=test_category.category_id))

    page1 = service.list(limit=3, offset=0)
    page2 = service.list(limit=3, offset=3)

    assert len(page1) == 3
    assert len(page2) == 2


def test_list_expenses_empty(test_db: Session, test_user: User):
    """List returns empty when user has no expenses"""
    service = ExpenseService(test_user, test_db)

    expenses = service.list(limit=100, offset=0)

    assert expenses == []
