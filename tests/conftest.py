import pytest
from sqlmodel import create_engine, Session, SQLModel
from app.auth import get_password_hash
from app.models import User, Expense
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_session
from sqlmodel.pool import StaticPool

@pytest.fixture
def test_db():
    print("Creating database")

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


@pytest.fixture    
def test_user(test_db: Session):

    print("Creating user in database")

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
    from app.auth import create_token

    user_id = test_user.user_id
    assert user_id is not None

    token = create_token(user_id)
    client.headers = {"Authorization": f"Bearer {token}"}

    return client

@pytest.fixture
def test_expense(test_db: Session, test_user: User):
    from datetime import date
    assert test_user.user_id is not None
    expense = Expense(
        name="Test Expense",
        amount=100.0,
        category="Test Category",
        date_of_entry=date.today(),
        user_id=test_user.user_id
    )
    test_db.add(expense)
    test_db.commit()
    test_db.refresh(expense)

    return expense