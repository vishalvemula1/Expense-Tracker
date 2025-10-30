import pytest
from sqlmodel import create_engine, Session, SQLModel
from app.auth import get_password_hash
from app.models import User, Expense, Category
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
def test_category(test_db: Session, test_user: User):
    from datetime import date
    assert test_user.user_id
    category = Category(name="Uncategorized",
                        user_id=test_user.user_id,
                        date_of_entry=date.today(),
                        tag="Black", #type: ignore
                        is_default=True)
    
    test_db.add(category)
    test_db.commit()
    test_db.refresh(category)

    return category

@pytest.fixture
def test_new_category(test_db: Session, test_user: User):
    from datetime import date
    assert test_user.user_id
    category = Category(name="First Category",
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

    from datetime import date

    assert test_user.user_id is not None
    assert test_category is not None
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

@pytest.fixture
def create_test_expenses_and_users(test_db: Session, test_user: User, test_category: Category):

    from datetime import date

    assert test_user.user_id is not None
    assert test_category is not None
    assert test_category.category_id is not None

    hashed_pw = get_password_hash("testpassword")

    new_user = User(
        username="newuser",
        email="newuser@example.com",
        salary=50000,
        password_hash=hashed_pw
    )

    test_db.add(new_user)
    test_db.commit()
    test_db.refresh(new_user)

    assert new_user.user_id is not None
    assert test_user.user_id is not None

    expenses = [
        Expense(name="Books", 
                amount=150, 
                description="Learning FastAPI", 
                category_id=test_category.category_id,
                date_of_entry=date.today(), 
                user_id=new_user.user_id),

        Expense(name="Laptop", 
                amount=1200, 
                description="Work laptop", 
                category_id=test_category.category_id,
                date_of_entry=date.today(), 
                user_id=test_user.user_id),
    ]

    expenses_2 = [
        Expense(name="Cheese", 
                amount=50, 
                description="Unforunate lack of judgement", 
                category_id=test_category.category_id,
                date_of_entry=date.today(), 
                user_id=new_user.user_id),

        Expense(name="Wine", 
                amount=100, 
                description="For the classy nights", 
                category_id=test_category.category_id,
                date_of_entry=date.today(), 
                user_id=test_user.user_id),

        Expense(name="Rent", 
                amount=1200, 
                description="Monthly rent", 
                category_id=test_category.category_id,
                date_of_entry=date.today(), 
                user_id=test_user.user_id),
    ]


    expenses.extend(expenses_2)
    test_db.add_all(expenses)
    test_db.commit()
    return expenses