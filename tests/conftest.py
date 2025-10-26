import pytest
from sqlmodel import create_engine, Session, SQLModel
from app.auth import get_password_hash
from app.models import User
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

