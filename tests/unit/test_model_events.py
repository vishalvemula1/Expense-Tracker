import pytest
from sqlmodel import Session, select
from app.models import User, UserCreate, Category, CategoryUpdate
from app.services.auth_service import AuthService
from app.services.category_service import CategoryService
from app.exceptions import AppExceptions
from datetime import date

def test_create_user_creates_default_category(test_db: Session):
    """
    Test that creating a user automatically creates a default 'Uncategorized' category.
    """
    # Create a user directly via SQLModel to test the event listener
    # (AuthService also uses SQLModel, but testing direct insertion is more robust for model events)
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

def test_prevent_default_category_update(test_db: Session, test_user: User):
    """
    Test that updating a default category raises AppExceptions.DefaultCategoryUneditable.
    """
    # Get the default category for the test user
    statement = select(Category).where(
        Category.user_id == test_user.user_id,
        Category.is_default == True
    )
    default_category = test_db.exec(statement).first()
    assert default_category is not None

    # Attempt to update it via Service (which triggers the event via session commit/flush)
    # Note: Service layer doesn't explicitly check anymore, so this tests the event listener
    category_service = CategoryService(test_user, test_db)
    update_request = CategoryUpdate(name="New Name")

    with pytest.raises(AppExceptions.DefaultCategoryUneditable.__class__) as exc_info:
        category_service.update(default_category.category_id, update_request)
    
    assert exc_info.value.status_code == 409

def test_prevent_default_category_delete(test_db: Session, test_user: User):
    """
    Test that deleting a default category raises AppExceptions.DefaultCategoryUneditable.
    """
    # Get the default category for the test user
    statement = select(Category).where(
        Category.user_id == test_user.user_id,
        Category.is_default == True
    )
    default_category = test_db.exec(statement).first()
    assert default_category is not None

    # Attempt to delete it via Service
    category_service = CategoryService(test_user, test_db)

    with pytest.raises(AppExceptions.DefaultCategoryUneditable.__class__) as exc_info:
        category_service.delete(default_category.category_id)

    assert exc_info.value.status_code == 409

def test_prevent_multiple_default_categories(test_db: Session, test_user: User):
    """
    Test that the database constraint prevents creating a second default category.
    This tests the partial unique index: uq_one_default_per_user.
    """
    from sqlalchemy.exc import IntegrityError
    
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

