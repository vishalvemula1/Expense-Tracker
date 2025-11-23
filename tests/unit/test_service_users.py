import pytest
from sqlmodel import Session
from fastapi import HTTPException
from app.services.user_service import UserService
from app.models import User, UserUpdate


# ====================================================================
# get_user (static): Retrieves user by ID
# ====================================================================

def test_get_user_success(test_db: Session, test_user: User):
    user = UserService.get_user(test_user.user_id, test_db)  # type: ignore

    assert user.user_id == test_user.user_id
    assert user.username == test_user.username


def test_get_user_not_found(test_db: Session):
    with pytest.raises(HTTPException) as exc_info:
        UserService.get_user(99999, test_db)

    assert exc_info.value.status_code == 404


# ====================================================================
# get: Returns current authenticated user
# ====================================================================

def test_get_current_user_success(test_db: Session, test_user: User):
    """get() should return the authenticated user"""
    service = UserService(test_user, test_db)

    user = service.get()

    assert user.user_id == test_user.user_id
    assert user.username == test_user.username
    assert user.email == test_user.email


# ====================================================================
# update: Partial updates and password hashing
# ====================================================================

def test_update_user_partial_fields(test_db: Session, test_user: User):
    """Update only some fields, others remain unchanged"""
    service = UserService(test_user, test_db)
    update_data = UserUpdate(username="updateduser", salary=75000)

    updated = service.update(update_data)

    assert updated.username == "updateduser"
    assert updated.salary == 75000
    assert updated.email == "test@example.com"  # Unchanged


def test_update_user_password_is_hashed(test_db: Session, test_user: User):
    """Password update should hash the new password"""
    service = UserService(test_user, test_db)
    old_hash = test_user.password_hash
    update_data = UserUpdate(password="newpassword123")

    updated = service.update(update_data)

    assert updated.password_hash != old_hash
    assert updated.password_hash != "newpassword123"


def test_update_user_duplicate_username(test_db: Session, test_user: User):
    """Cannot update to a username that already exists"""
    # Create another user
    from app.services.auth_service import AuthService
    from app.models import UserCreate

    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    # Try to update test_user's username to otheruser's
    service = UserService(test_user, test_db)
    update_data = UserUpdate(username="otheruser")

    with pytest.raises(HTTPException) as exc_info:
        service.update(update_data)

    assert exc_info.value.status_code == 409
    assert "Username already exists" in exc_info.value.detail


def test_update_user_duplicate_email(test_db: Session, test_user: User):
    """Cannot update to an email that already exists"""
    from app.services.auth_service import AuthService
    from app.models import UserCreate

    auth_service = AuthService(test_db)
    other_user = auth_service.create_user_with_defaults(UserCreate(
        username="otheruser",
        email="other@example.com",
        salary=50000,
        password="password123"
    ))

    service = UserService(test_user, test_db)
    update_data = UserUpdate(email="other@example.com")

    with pytest.raises(HTTPException) as exc_info:
        service.update(update_data)

    assert exc_info.value.status_code == 409
    assert "Email already exists" in exc_info.value.detail


def test_update_user_empty_update(test_db: Session, test_user: User):
    """Empty update should not change anything"""
    service = UserService(test_user, test_db)
    original_username = test_user.username
    update_data = UserUpdate()

    updated = service.update(update_data)

    assert updated.username == original_username


# ====================================================================
# delete: Removes user from database
# ====================================================================

def test_delete_user_success(test_db: Session, test_user: User):
    user_id = test_user.user_id
    service = UserService(test_user, test_db)

    service.delete()

    # Verify user is gone
    with pytest.raises(HTTPException) as exc_info:
        UserService.get_user(user_id, test_db)  # type: ignore

    assert exc_info.value.status_code == 404


def test_delete_user_cascades_to_categories_and_expenses(test_db: Session, test_user: User):
    """Deleting a user should cascade delete their categories and expenses"""
    from app.services.category_service import CategoryService
    from app.services.expense_service import ExpenseService
    from app.models import CategoryCreate, ExpenseCreate
    from sqlmodel import select
    from app.models import Category, Expense
    
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
