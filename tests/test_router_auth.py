from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User


# ====================================================================
# Testing for the signup (post) endpoint in users.py
# ====================================================================
def test_signup_happy_path(client: TestClient, test_db: Session):
    response = client.post("/auth/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "salary": 60000,
        "password": "securepass123"
    })

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "new@example.com"
    assert data["salary"] == 60000
    assert "password" not in data

def test_signup_duplicate_name(client: TestClient, test_db: Session, test_user):
    response  = client.post("/auth/signup", json={
        "username": "testuser",
        "email": "new@example.com",
        "salary": 5000,
        "password": "securepass123"
    })

    assert response.status_code == 409
    data = response.json()
    assert data['detail'] == "Username already exists"

def test_signup_duplicate_email(client: TestClient, test_db: Session, test_user):
    response  = client.post("/auth/signup", json={
        "username": "newuser",
        "email": "test@example.com",
        "salary": 5000,
        "password": "securepass123"
    })

    assert response.status_code == 409
    data = response.json()
    assert data['detail'] == "Email already exists"

def test_signup_empty_username(client: TestClient):
    response = client.post("/auth/signup", json={
        "username": "",
        "email": "new@example.com",
        "salary": 50000,
        "password": "securepass123"
    })
    
    assert response.status_code == 422 
    data = response.json()   
    assert "username cannot be empty or whitespace only" in data["detail"][0]["msg"]
    
def test_signup_empty_password(client: TestClient):
    response = client.post("/auth/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "salary": 50000,
        "password": ""
    })
    
    assert response.status_code == 422
    data = response.json()   
    assert "password cannot be empty or whitespace only" in data["detail"][0]["msg"]

def test_signup_negative_salary(client: TestClient):
    response = client.post("/auth/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "salary": -5000,
        "password": "pass123"
    })
    
    assert response.status_code == 422


# ====================================================================
# Testing for the login endpoint in users.py (post)
# ====================================================================

def test_login_happy_path(client: TestClient, test_user: User):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "testpassword"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user: User):
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

def test_login_user_not_found(client: TestClient):
    response = client.post("/auth/login", data={
        "username": "nonexistentuser",
        "password": "somepassword"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

# ====================================================================
# Testing for default category creation on signup
# ====================================================================

def test_signup_creates_default_category(client: TestClient, test_db: Session):
    from sqlmodel import select
    from app.models import Category

    response = client.post("/auth/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "salary": 60000,
        "password": "securepass123"
    })

    assert response.status_code == 200
    user_data = response.json()
    user_id = user_data["user_id"]

    # Check that default category was created
    statement = select(Category).where(
        Category.user_id == user_id,
        Category.is_default == True
    )
    default_category = test_db.exec(statement).first()

    assert default_category is not None
    assert default_category.name == "Uncategorized"
    assert default_category.description == "All your uncategorized expenses"
    assert default_category.is_default == True
    assert default_category.tag == "Black"