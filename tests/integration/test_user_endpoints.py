"""
Integration tests for user endpoints (/me).

These tests verify:
- User profile retrieval
- User profile updates
- User deletion

NOTE: Cascade delete tests are in unit/test_user_service.py
"""
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User


class TestUserProfile:

    def test_get_current_user_profile(self, authenticated_client: TestClient, test_user: User):
        response = authenticated_client.get("/me")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["salary"] == test_user.salary
        assert data["user_id"] == test_user.user_id


class TestUserUpdate:

    def test_update_user_profile(self, authenticated_client: TestClient, test_user: User, test_db: Session):
        response = authenticated_client.put("/me", json={
            "username": "updated_username",
            "email": "updated@example.com",
            "salary": 75000
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == "updated_username"
        assert data["email"] == "updated@example.com"
        assert data["salary"] == 75000
        
        test_db.refresh(test_user)
        assert test_user.username == "updated_username"
        assert test_user.email == "updated@example.com"
        assert test_user.salary == 75000

    def test_partial_update_user_profile(self, authenticated_client: TestClient, test_user: User, test_db: Session):
        original_username = test_user.username
        original_email = test_user.email
        
        response = authenticated_client.put("/me", json={
            "salary": 80000
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["salary"] == 80000
        assert data["username"] == original_username
        assert data["email"] == original_email


class TestUserDeletion:

    def test_delete_user_removes_from_database(
        self, 
        authenticated_client: TestClient, 
        test_user: User, 
        test_db: Session
    ):
        user_id = test_user.user_id
        
        response = authenticated_client.delete("/me")
        
        assert response.status_code == 200
        
        deleted_user = test_db.get(User, user_id)
        assert deleted_user is None


class TestMultiUserIsolation:

    def test_user_only_sees_own_profile(
        self,
        user1_client: TestClient,
        user2_client: TestClient,
        multi_user_data
    ):
        response1 = user1_client.get("/me")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["username"] == multi_user_data.user1.username
        
        response2 = user2_client.get("/me")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["username"] == multi_user_data.user2.username
        
        assert data1["user_id"] != data2["user_id"]

