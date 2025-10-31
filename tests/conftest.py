import pytest
from sqlmodel import create_engine, Session, SQLModel
from app.auth import get_password_hash, create_token
from app.models import User, Expense, Category
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session
from sqlmodel.pool import StaticPool
from datetime import date
from typing import NamedTuple

# ====================================================================
# Basic Fixtures
# ====================================================================

@pytest.fixture
def test_db():
    engine = create_engine("sqlite:///:memory:",
                           connect_args={"check_same_thread": False},
                           poolclass=StaticPool)

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session


@pytest.fixture
def client(test_db: Session):
    app.dependency_overrides[get_session] = lambda: test_db
    yield TestClient(app)
    app.dependency_overrides.clear()

# ====================================================================
# Single User Fixtures
# ====================================================================

@pytest.fixture
def test_user(test_db: Session):
    hashed_pw = get_password_hash("testpassword")
    test_user = User(
        username="testuser",
        email="test@example.com",
        salary=50000,
        password_hash=hashed_pw
    )

    test_db.add(test_user)
    test_db.commit()
    test_db.refresh(test_user)

    return test_user

@pytest.fixture
def authenticated_client(client: TestClient, test_user: User):
    user_id = test_user.user_id
    assert user_id is not None

    token = create_token(user_id)
    client.headers = {"Authorization": f"Bearer {token}"}

    return client

@pytest.fixture
def test_category(test_db: Session, test_user: User):
    assert test_user.user_id
    category = Category(
        name="Uncategorized",
        user_id=test_user.user_id,
        date_of_entry=date.today(),
        tag="Black", #type: ignore
        is_default=True
    )

    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    return category

@pytest.fixture
def test_new_category(test_db: Session, test_user: User):
    assert test_user.user_id
    category = Category(
        name="First Category",
        user_id=test_user.user_id,
        date_of_entry=date.today(),
        tag="Blue" #type: ignore
    )

    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    return category


@pytest.fixture
def test_expense(test_db: Session, test_user: User, test_category: Category):
    assert test_user.user_id is not None
    assert test_category.category_id is not None

    expense = Expense(
        name="Test Expense",
        amount=100.0,
        category_id=test_category.category_id,
        date_of_entry=date.today(),
        user_id=test_user.user_id
    )

    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)

    return expense

# ====================================================================
# Multi-User Test Data Fixtures
# ====================================================================

class MultiUserData(NamedTuple):
    """Container for multi-user test data"""
    user1: User
    user2: User
    user1_default_category: Category
    user2_default_category: Category
    user1_food_category: Category
    user2_travel_category: Category
    user1_expenses: list[Expense]
    user2_expenses: list[Expense]

@pytest.fixture
def multi_user_data(test_db: Session) -> MultiUserData:
    """Creates 2 users with categories and expenses for security testing"""
    hashed_pw = get_password_hash("testpassword")

    # Create User 1
    user1 = User(
        username="user1",
        email="user1@example.com",
        salary=60000,
        password_hash=hashed_pw
    )
    test_db.add(user1)
    test_db.commit()
    test_db.refresh(user1)
    assert user1.user_id is not None

    # Create User 2
    user2 = User(
        username="user2",
        email="user2@example.com",
        salary=70000,
        password_hash=hashed_pw
    )
    test_db.add(user2)
    test_db.commit()
    test_db.refresh(user2)
    assert user2.user_id is not None

    # Create categories for User 1
    user1_default_cat = Category(
        name="Uncategorized",
        user_id=user1.user_id,
        is_default=True,
        tag="Black", #type: ignore
        date_of_entry=date.today()
    )
    user1_food_cat = Category(
        name="Food",
        user_id=user1.user_id,
        tag="Blue", #type: ignore
        date_of_entry=date.today()
    )

    # Create categories for User 2
    user2_default_cat = Category(
        name="Uncategorized",
        user_id=user2.user_id,
        is_default=True,
        tag="Black", #type: ignore
        date_of_entry=date.today()
    )
    user2_travel_cat = Category(
        name="Travel",
        user_id=user2.user_id,
        tag="Red", #type: ignore
        date_of_entry=date.today()
    )

    test_db.add_all([user1_default_cat, user1_food_cat, user2_default_cat, user2_travel_cat])
    test_db.commit()
    test_db.refresh(user1_default_cat)
    test_db.refresh(user1_food_cat)
    test_db.refresh(user2_default_cat)
    test_db.refresh(user2_travel_cat)

    assert user1_default_cat.category_id is not None
    assert user1_food_cat.category_id is not None
    assert user2_default_cat.category_id is not None
    assert user2_travel_cat.category_id is not None

    # Create expenses for User 1
    user1_expenses = [
        Expense(
            name="Groceries",
            amount=50.0,
            category_id=user1_food_cat.category_id,
            user_id=user1.user_id,
            date_of_entry=date.today()
        ),
        Expense(
            name="Coffee",
            amount=5.0,
            category_id=user1_default_cat.category_id,
            user_id=user1.user_id,
            date_of_entry=date.today()
        ),
    ]

    # Create expenses for User 2
    user2_expenses = [
        Expense(
            name="Flight",
            amount=300.0,
            category_id=user2_travel_cat.category_id,
            user_id=user2.user_id,
            date_of_entry=date.today()
        ),
        Expense(
            name="Misc",
            amount=20.0,
            category_id=user2_default_cat.category_id,
            user_id=user2.user_id,
            date_of_entry=date.today()
        ),
    ]

    test_db.add_all(user1_expenses + user2_expenses)
    test_db.commit()
    for expense in user1_expenses + user2_expenses:
        test_db.refresh(expense)
        assert expense.expense_id is not None

    return MultiUserData(
        user1=user1,
        user2=user2,
        user1_default_category=user1_default_cat,
        user2_default_category=user2_default_cat,
        user1_food_category=user1_food_cat,
        user2_travel_category=user2_travel_cat,
        user1_expenses=user1_expenses,
        user2_expenses=user2_expenses
    )

@pytest.fixture
def user1_client(client: TestClient, multi_user_data: MultiUserData):
    """Authenticated client for user1"""
    assert multi_user_data.user1.user_id
    token = create_token(multi_user_data.user1.user_id)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client

@pytest.fixture
def user2_client(client: TestClient, multi_user_data: MultiUserData):
    """Authenticated client for user2"""
    assert multi_user_data.user2.user_id
    token = create_token(multi_user_data.user2.user_id)
    client.headers = {"Authorization": f"Bearer {token}"}
    return client