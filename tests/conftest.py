import pytest
from sqlmodel import create_engine, Session, SQLModel
from app.auth import get_password_hash
from app.models import User


@pytest.fixture
def test_db():
    print("Creating database")

    engine = create_engine("sqlite:///:memory:")

    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

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

    return test_user

