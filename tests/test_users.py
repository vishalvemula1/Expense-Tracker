from fastapi.testclient import TestClient
from app.main import app
from sqlmodel import Session
from app.models import User

#Post
# ====================================================================
# Testing for the signup (post) endpoint in users.py
# ====================================================================
def test_signup_happy_path(client: TestClient, test_db: Session):
    response = client.post("/users/signup", json={
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
    response  = client.post("/users/signup", json={
        "username": "testuser",
        "email": "new@example.com",
        "salary": 5000,
        "password": "securepass123"
    })

    assert response.status_code == 409
    data = response.json()
    assert data['detail'] == "Username or email already exists"

def test_signup_duplicate_email(client: TestClient, test_db: Session, test_user):    
    response  = client.post("/users/signup", json={
        "username": "newuser",
        "email": "test@example.com",
        "salary": 5000,
        "password": "securepass123"
    })

    assert response.status_code == 409
    data = response.json()
    assert data['detail'] == "Username or email already exists"

def test_signup_empty_username(client: TestClient):
    response = client.post("/users/signup", json={
        "username": "",
        "email": "new@example.com",
        "salary": 50000,
        "password": "securepass123"
    })
    
    assert response.status_code == 422 
    data = response.json()   
    assert "Cannot be empty or whitespace only" in data["detail"][0]["msg"]
    
def test_signup_empty_password(client: TestClient):
    response = client.post("/users/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "salary": 50000,
        "password": ""
    })
    
    assert response.status_code == 422
    data = response.json()   
    assert "Cannot be empty or whitespace only" in data["detail"][0]["msg"]

def test_signup_negative_salary(client: TestClient):
    response = client.post("/users/signup", json={
        "username": "newuser",
        "email": "new@example.com",
        "salary": -5000,
        "password": "pass123"
    })
    
    assert response.status_code == 422

# ====================================================================
# Testing for the read user (get) endpoint in users.py
# ====================================================================

def test_read_user_happy_path(authenticated_client: TestClient,  
                              test_user: User):

    user_id = test_user.user_id
    assert user_id is not None

    response = authenticated_client.get(f"/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_read_user_unauthenticated(client: TestClient,
                                 test_user: User):

    user_id = test_user.user_id
    assert user_id is not None

    response = client.get(f"/users/{user_id}")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_read_user_unauthorized(authenticated_client: TestClient):
    response = authenticated_client.get("/users/3")

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"


# ====================================================================
# Testing for the update_user (put) endpoint in users.py
# ====================================================================

def test_update_user_happy_path(authenticated_client: TestClient,
                               test_user: User):

    user_id = test_user.user_id
    assert user_id is not None

    response = authenticated_client.put(f"/users/{user_id}", json={
        "email": "updated@example.com",
        "salary": 60000
    })

    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "updated@example.com"
    assert data["salary"] == 60000
    assert "password" not in data

def test_update_user_unauthenticated(client: TestClient,
                                 test_user: User):

    user_id = test_user.user_id
    assert user_id is not None

    response = client.put(f"/users/{user_id}", json={
        "email": "updated@example.com",
        "salary": 60000
    })

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_update_user_unauthorized(authenticated_client: TestClient):
    response = authenticated_client.put("/users/3", json={
        "email": "updated@example.com", 
        "salary": 60000
    })

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

def test_update_user_duplicate_username(authenticated_client: TestClient,
                                        test_db: Session,
                                        test_user: User):
    from app.auth import get_password_hash
    # Create another user to cause a duplicate username conflict
    hashed_pw = get_password_hash("testpassword")
    another_user = User(
        username="existinguser",
        email="existing@example.com",
        password_hash=hashed_pw,
        salary=50000
    )
    test_db.add(another_user)
    test_db.commit()

    response = authenticated_client.put(f"/users/{test_user.user_id}", json={
        "username": "existinguser"
    })

    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Username or email already exists"

# ====================================================================
# Testing for the delete_user (delete) endpoint in users.py
# ====================================================================

def test_delete_user_happy_path(authenticated_client: TestClient,
                               test_user: User):

    user_id = test_user.user_id
    assert user_id is not None

    response = authenticated_client.delete(f"/users/{user_id}")

    assert response.status_code == 200
    data = response.json()
    assert data == "Deletion Successful"

def test_delete_user_unauthenticated(client: TestClient,
                                 test_user: User):

    user_id = test_user.user_id
    assert user_id is not None

    response = client.delete(f"/users/{user_id}")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_delete_user_unauthorized(authenticated_client: TestClient):
    response = authenticated_client.delete("/users/3")

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

# ====================================================================
# Testing for the login endpoint in users.py (post)
# ====================================================================

def test_login_happy_path(client: TestClient, test_user: User):
    response = client.post("/users/login", data={
        "username": "testuser",
        "password": "testpassword"
    })

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client: TestClient, test_user: User):
    response = client.post("/users/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

def test_login_user_not_found(client: TestClient):
    response = client.post("/users/login", data={
        "username": "nonexistentuser",
        "password": "somepassword"
    })

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Invalid username or password"

