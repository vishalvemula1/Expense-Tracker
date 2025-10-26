from fastapi.testclient import TestClient
from app.main import app
from sqlmodel import Session


# ====================================================================
# Testing for the signup endpoint in users.py
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

