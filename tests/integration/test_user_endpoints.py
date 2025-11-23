"""
Integration tests for user endpoints (/me).

These tests verify:
- User profile retrieval
- User profile updates
- User deletion with cascading effects
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import User, Category, Expense


class TestUserProfile:
    """Test /me endpoint for retrieving user profile"""

    def test_get_current_user_profile(self, authenticated_client: TestClient, test_user: User):
        """GET /me returns authenticated user's profile"""
        response = authenticated_client.get("/me")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["username"] == test_user.username
        assert data["email"] == test_user.email
        assert data["salary"] == test_user.salary
        assert data["user_id"] == test_user.user_id


class TestUserUpdate:
    """Test PUT /me for updating user profile"""

    def test_update_user_profile(self, authenticated_client: TestClient, test_user: User, test_db: Session):
        """PUT /me updates user profile and persists changes"""
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
        
        # Verify changes persisted in database
        test_db.refresh(test_user)
        assert test_user.username == "updated_username"
        assert test_user.email == "updated@example.com"
        assert test_user.salary == 75000

    def test_partial_update_user_profile(self, authenticated_client: TestClient, test_user: User, test_db: Session):
        """Can update only salary, leaving other fields unchanged"""
        original_username = test_user.username
        original_email = test_user.email
        
        response = authenticated_client.put("/me", json={
            "salary": 80000
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["salary"] == 80000
        assert data["username"] == original_username  # Unchanged
        assert data["email"] == original_email  # Unchanged


class TestUserDeletion:
    """Test DELETE /me for user account deletion"""

    def test_delete_user_removes_from_database(
        self, 
        authenticated_client: TestClient, 
        test_user: User, 
        test_db: Session
    ):
        """DELETE /me removes user from database"""
        user_id = test_user.user_id
        
        response = authenticated_client.delete("/me")
        
        assert response.status_code == 200
        
        # Verify user no longer exists
        deleted_user = test_db.get(User, user_id)
        assert deleted_user is None

    def test_delete_user_cascades_to_categories_and_expenses(
        self, 
        authenticated_client: TestClient, 
        test_user: User,
        test_category: Category,
        test_expense: Expense,
        test_db: Session
    ):
        """Deleting user cascades to delete their categories and expenses"""
        category_id = test_category.category_id
        expense_id = test_expense.expense_id
        
        response = authenticated_client.delete("/me")
        
        assert response.status_code == 200
        
        # Verify categories deleted
        deleted_category = test_db.get(Category, category_id)
        assert deleted_category is None
        
        # Verify expenses deleted
        deleted_expense = test_db.get(Expense, expense_id)
        assert deleted_expense is None


class TestMultiUserIsolation:
    """Test that users cannot access other users' profiles"""

    def test_user_only_sees_own_profile(
        self,
        user1_client: TestClient,
        user2_client: TestClient,
        multi_user_data
    ):
        """Each user sees only their own profile via /me"""
        # User 1 gets their profile
        response1 = user1_client.get("/me")
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["username"] == multi_user_data.user1.username
        
        # User 2 gets their profile
        response2 = user2_client.get("/me")
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["username"] == multi_user_data.user2.username
        
        # Profiles are different
        assert data1["user_id"] != data2["user_id"]
