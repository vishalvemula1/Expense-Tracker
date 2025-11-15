from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User, UserCreate
from app.services.auth_service import AuthService



# ====================================================================
# Testing for the read user (get) endpoint in users.py
# ====================================================================

def test_read_user_happy_path(authenticated_client: TestClient,  
                              test_user: User):

    response = authenticated_client.get("/me")

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"

def test_read_user_unauthenticated(client: TestClient,
                                 test_user: User):

    response = client.get("/me")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"


# ====================================================================
# Testing for the update_user (put) endpoint in users.py
# ====================================================================

def test_update_user_happy_path(authenticated_client: TestClient,
                               test_user: User):

    response = authenticated_client.put("/me", json={
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

    response = client.put("/me", json={
        "email": "updated@example.com",
        "salary": 60000
    })

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_update_user_duplicate_username(authenticated_client: TestClient,
                                        test_db: Session,
                                        test_user: User):
    auth_service = AuthService(test_db)
    auth_service.create_user_with_defaults(UserCreate(
        username="existinguser",
        email="existing@example.com",
        password="testpassword",
        salary=50000
    ))

    response = authenticated_client.put("/me", json={
        "username": "existinguser"
    })

    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Username already exists"

# ====================================================================
# Testing for the delete_user (delete) endpoint in users.py
# ====================================================================

def test_delete_user_happy_path(authenticated_client: TestClient,
                               test_user: User):

    response = authenticated_client.delete("/me")

    assert response.status_code == 200
    assert response.json() is None

def test_delete_user_unauthenticated(client: TestClient,
                                 test_user: User):

    response = client.delete("/me")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"



