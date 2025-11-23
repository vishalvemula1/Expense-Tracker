"""
Integration tests for category endpoints (/me/categories).

These tests verify:
- Category CRUD operations via HTTP
- Category listing with pagination
- Category-expense relationship queries
- Multi-user data isolation
"""
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from app.models import Category, Expense


class TestCategoryCreation:
    """Test POST /me/categories"""

    def test_create_category_persists_to_database(
        self, 
        authenticated_client: TestClient,
        test_user,
        test_db: Session
    ):
        """Creating category via API persists to database"""
        response = authenticated_client.post("/me/categories/", json={
            "name": "Entertainment",
            "tag": "Blue"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Entertainment"
        assert data["tag"] == "Blue"
        assert "category_id" in data
        
        # Verify in database
        category = test_db.get(Category, data["category_id"])
        assert category is not None
        assert category.name == "Entertainment"
        assert category.user_id == test_user.user_id


class TestCategoryRetrieval:
    """Test GET /me/categories/{category_id}"""

    def test_get_category_by_id(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category
    ):
        """Can retrieve specific category by ID"""
        response = authenticated_client.get(
            f"/me/categories/{test_custom_category.category_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category_id"] == test_custom_category.category_id
        assert data["name"] == test_custom_category.name

    def test_get_nonexistent_category_fails(self, authenticated_client: TestClient):
        """Getting non-existent category returns 404"""
        response = authenticated_client.get("/me/categories/99999")
        
        assert response.status_code == 404


class TestCategoryListing:
    """Test GET /me/categories/ with pagination"""

    def test_list_categories_default_pagination(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_custom_category: Category
    ):
        """List categories returns categories for authenticated user"""
        response = authenticated_client.get("/me/categories/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2  # At least default + custom category
        
        # Verify categories belong to user
        category_names = [cat["name"] for cat in data]
        assert test_category.name in category_names
        assert test_custom_category.name in category_names

    def test_list_categories_with_limit(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_custom_category: Category
    ):
        """Limit parameter controls number of results"""
        response = authenticated_client.get("/me/categories/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1


class TestCategoryUpdate:
    """Test PUT /me/categories/{category_id}"""

    def test_update_category_persists_changes(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category,
        test_db: Session
    ):
        """Updating category via API persists changes"""
        response = authenticated_client.put(
            f"/me/categories/{test_custom_category.category_id}",
            json={"name": "Updated Name", "tag": "Red"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Name"
        assert data["tag"] == "Red"
        
        # Verify in database
        test_db.refresh(test_custom_category)
        assert test_custom_category.name == "Updated Name"
        assert test_custom_category.tag == "Red"


class TestCategoryDeletion:
    """Test DELETE /me/categories/{category_id}"""

    def test_delete_category_removes_from_database(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category,
        test_db: Session
    ):
        """Deleting category removes it from database"""
        category_id = test_custom_category.category_id
        
        response = authenticated_client.delete(f"/me/categories/{category_id}")
        
        assert response.status_code == 200
        
        # Verify category deleted
        deleted = test_db.get(Category, category_id)
        assert deleted is None


class TestCategoryExpenses:
    """Test GET /me/categories/{category_id}/expenses"""

    def test_get_category_expenses(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_expense: Expense
    ):
        """Can retrieve all expenses for a category"""
        response = authenticated_client.get(
            f"/me/categories/{test_category.category_id}/expenses"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify expense data
        expense_ids = [exp["expense_id"] for exp in data]
        assert test_expense.expense_id in expense_ids


class TestMultiUserCategoryIsolation:
    """Test that users cannot access other users' categories"""

    def test_user_cannot_view_other_users_category(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """User 1 cannot access User 2's category"""
        user2_category_id = multi_user_data.user2_travel_category.category_id
        
        response = user1_client.get(f"/me/categories/{user2_category_id}")
        
        assert response.status_code == 403

    def test_user_cannot_update_other_users_category(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """User 1 cannot update User 2's category"""
        user2_category_id = multi_user_data.user2_travel_category.category_id
        
        response = user1_client.put(
            f"/me/categories/{user2_category_id}",
            json={"name": "Hacked"}
        )
        
        assert response.status_code == 403

    def test_user_cannot_delete_other_users_category(
        self,
        user1_client: TestClient,
        multi_user_data,
        test_db: Session
    ):
        """User 1 cannot delete User 2's category"""
        user2_category_id = multi_user_data.user2_travel_category.category_id
        
        response = user1_client.delete(f"/me/categories/{user2_category_id}")
        
        assert response.status_code == 403
        
        # Verify category still exists
        category = test_db.get(Category, user2_category_id)
        assert category is not None

    def test_list_categories_only_shows_own_categories(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """List endpoint only returns authenticated user's categories"""
        response = user1_client.get("/me/categories/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have user1's categories
        category_names = [cat["name"] for cat in data]
        assert multi_user_data.user1_food_category.name in category_names
        
        # Should NOT have user2's categories
        assert multi_user_data.user2_travel_category.name not in category_names
