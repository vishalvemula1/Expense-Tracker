import pytest
from sqlmodel import Session
from fastapi import HTTPException
from app.services.category_service import CategoryService
from app.services.auth_service import AuthService
from app.models import User, Category, CategoryCreate, CategoryUpdate, UserCreate, Expense
from datetime import date


# ====================================================================
# create: Creates category for user
# ====================================================================

def test_create_category_success(test_db: Session, test_user: User):
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


def test_create_category_duplicate_name(test_db: Session, test_user: User):
    """Category names must be unique per user"""
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


def test_create_category_same_name_different_users(test_db: Session, test_user: User):
    """Different users can have categories with the same name"""
    # Create category for test_user
    service1 = CategoryService(test_user, test_db)
    service1.create(CategoryCreate(name="Food", tag="Blue"))

    # Create another user
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    # Other user can also have "Food" category
    service2 = CategoryService(other_user, test_db)
    category = service2.create(CategoryCreate(name="Food", tag="Red"))

    assert category.name == "Food"
    assert category.user_id == other_user.user_id


# ====================================================================
# get: Retrieves category with ownership check
# ====================================================================

def test_get_category_success(test_db: Session, test_user: User, test_custom_category: Category):
    service = CategoryService(test_user, test_db)

    category = service.get(test_custom_category.category_id)  # type: ignore

    assert category.category_id == test_custom_category.category_id


def test_get_category_not_found(test_db: Session, test_user: User):
    service = CategoryService(test_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get(99999)

    assert exc_info.value.status_code == 404


def test_get_category_wrong_owner(test_db: Session, test_user: User, test_custom_category: Category):
    """User cannot access another user's category"""
    # Create another user
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    # Other user tries to access test_user's category
    service = CategoryService(other_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get(test_custom_category.category_id)  # type: ignore

    assert exc_info.value.status_code == 403


# ====================================================================
# update: Updates category with default protection
# ====================================================================

def test_update_category_success(test_db: Session, test_user: User, test_custom_category: Category):
    service = CategoryService(test_user, test_db)
    update_data = CategoryUpdate(name="Updated Name", tag="Red")

    updated = service.update(test_custom_category.category_id, update_data)  # type: ignore

    assert updated.name == "Updated Name"
    assert updated.tag == "Red"


def test_update_default_category_conflict(test_db: Session, test_user: User, test_category: Category):
    """Cannot update the default category"""
    service = CategoryService(test_user, test_db)
    update_data = CategoryUpdate(name="New Name")

    with pytest.raises(HTTPException) as exc_info:
        service.update(test_category.category_id, update_data)  # type: ignore

    assert exc_info.value.status_code == 409


def test_update_category_duplicate_name(test_db: Session, test_user: User, test_custom_category: Category):
    """Cannot update to a name that already exists for this user"""
    service = CategoryService(test_user, test_db)

    # Create another category
    other_cat = service.create(CategoryCreate(name="Other", tag="White"))

    # Try to rename test_custom_category to "Other"
    update_data = CategoryUpdate(name="Other")

    with pytest.raises(HTTPException) as exc_info:
        service.update(test_custom_category.category_id, update_data)  # type: ignore

    assert exc_info.value.status_code == 409


def test_update_category_wrong_owner(test_db: Session, test_user: User, test_custom_category: Category):
    """Cannot update another user's category"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = CategoryService(other_user, test_db)
    update_data = CategoryUpdate(name="Hacked")

    with pytest.raises(HTTPException) as exc_info:
        service.update(test_custom_category.category_id, update_data)  # type: ignore

    assert exc_info.value.status_code == 403


def test_update_category_partial_name_only(test_db: Session, test_user: User, test_custom_category: Category):
    """Partial update: only update name, other fields unchanged"""
    service = CategoryService(test_user, test_db)
    original_tag = test_custom_category.tag

    update_data = CategoryUpdate(name="Partially Updated")

    updated = service.update(test_custom_category.category_id, update_data)  # type: ignore

    assert updated.name == "Partially Updated"
    assert updated.tag == original_tag


def test_update_category_partial_tag_only(test_db: Session, test_user: User, test_custom_category: Category):
    """Partial update: only update tag, other fields unchanged"""
    service = CategoryService(test_user, test_db)
    original_name = test_custom_category.name

    update_data = CategoryUpdate(tag="Black")

    updated = service.update(test_custom_category.category_id, update_data)  # type: ignore

    assert updated.tag == "Black"
    assert updated.name == original_name


def test_update_category_not_found(test_db: Session, test_user: User):
    """Cannot update non-existent category"""
    service = CategoryService(test_user, test_db)
    update_data = CategoryUpdate(name="Ghost")

    with pytest.raises(HTTPException) as exc_info:
        service.update(99999, update_data)

    assert exc_info.value.status_code == 404


# ====================================================================
# delete: Deletes category with default protection
# ====================================================================

def test_delete_category_success(test_db: Session, test_user: User, test_custom_category: Category):
    service = CategoryService(test_user, test_db)
    category_id = test_custom_category.category_id

    service.delete(category_id)  # type: ignore

    # Verify deleted
    with pytest.raises(HTTPException) as exc_info:
        service.get(category_id)  # type: ignore

    assert exc_info.value.status_code == 404


def test_delete_default_category_conflict(test_db: Session, test_user: User, test_category: Category):
    """Cannot delete the default category"""
    service = CategoryService(test_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(test_category.category_id)  # type: ignore

    assert exc_info.value.status_code == 409


def test_delete_category_wrong_owner(test_db: Session, test_user: User, test_custom_category: Category):
    """Cannot delete another user's category"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = CategoryService(other_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(test_custom_category.category_id)  # type: ignore

    assert exc_info.value.status_code == 403


def test_delete_category_not_found(test_db: Session, test_user: User):
    """Cannot delete non-existent category"""
    service = CategoryService(test_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.delete(99999)

    assert exc_info.value.status_code == 404


def test_delete_category_cascades_to_expenses(test_db: Session, test_user: User, test_custom_category: Category):
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


# ====================================================================
# list: Returns user's categories with pagination
# ====================================================================

def test_list_categories_returns_only_own(test_db: Session, test_user: User):
    """List should only return the current user's categories"""
    service = CategoryService(test_user, test_db)

    # Create some categories
    service.create(CategoryCreate(name="Food", tag="Blue"))
    service.create(CategoryCreate(name="Travel", tag="Red"))

    # Create another user with a category
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))
    other_service = CategoryService(other_user, test_db)
    other_service.create(CategoryCreate(name="Other's Cat", tag="Black"))

    # List test_user's categories
    categories = service.list(limit=100, offset=0)

    # Should have default + 2 created = 3
    assert len(categories) == 3
    assert all(c.user_id == test_user.user_id for c in categories)


def test_list_categories_pagination(test_db: Session, test_user: User):
    service = CategoryService(test_user, test_db)

    # Create 5 categories
    for i in range(5):
        service.create(CategoryCreate(name=f"Cat{i}", tag="Blue"))

    # Total: 1 default + 5 = 6
    page1 = service.list(limit=3, offset=0)
    page2 = service.list(limit=3, offset=3)

    assert len(page1) == 3
    assert len(page2) == 3


# ====================================================================
# get_expenses: Returns expenses for a category
# ====================================================================

def test_get_expenses_success(test_db: Session, test_user: User, test_category: Category, test_expense: Expense):
    service = CategoryService(test_user, test_db)

    expenses = service.get_expenses(test_category.category_id)  # type: ignore

    assert len(expenses) == 1
    assert expenses[0].expense_id == test_expense.expense_id


def test_get_expenses_empty_category(test_db: Session, test_user: User, test_custom_category: Category):
    service = CategoryService(test_user, test_db)

    expenses = service.get_expenses(test_custom_category.category_id)  # type: ignore

    assert expenses == []


def test_get_expenses_wrong_owner(test_db: Session, test_user: User, test_category: Category):
    """Cannot get expenses from another user's category"""
    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = CategoryService(other_user, test_db)

    with pytest.raises(HTTPException) as exc_info:
        service.get_expenses(test_category.category_id)  # type: ignore

    assert exc_info.value.status_code == 403
