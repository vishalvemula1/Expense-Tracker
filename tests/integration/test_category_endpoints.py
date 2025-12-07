"""
Integration tests for category endpoints (/me/categories).

These tests verify:
- Category CRUD operations via HTTP
- Category listing with pagination
- Category-expense relationship queries

NOTE: Multi-user isolation (403) tests are in unit/test_cross_user_security.py
"""
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import Category, Expense


class TestCategoryCreation:

    def test_create_category_persists_to_database(
        self, 
        authenticated_client: TestClient,
        test_user,
        test_db: Session
    ):
        response = authenticated_client.post("/me/categories/", json={
            "name": "Entertainment",
            "tag": "Blue"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "entertainment"
        assert data["tag"] == "Blue"
        assert "category_id" in data
        
        category = test_db.get(Category, data["category_id"])
        assert category is not None
        assert category.name == "entertainment"
        assert category.user_id == test_user.user_id


class TestCategoryRetrieval:

    def test_get_category_by_id(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category
    ):
        response = authenticated_client.get(
            f"/me/categories/{test_custom_category.category_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category_id"] == test_custom_category.category_id
        assert data["name"] == test_custom_category.name

    def test_get_nonexistent_category_fails(self, authenticated_client: TestClient):
        response = authenticated_client.get("/me/categories/99999")
        
        assert response.status_code == 404


class TestCategoryListing:

    def test_list_categories_default_pagination(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_custom_category: Category
    ):
        response = authenticated_client.get("/me/categories/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 2
        
        category_names = [cat["name"] for cat in data]
        assert test_category.name in category_names
        assert test_custom_category.name in category_names

    def test_list_categories_with_limit(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_custom_category: Category
    ):
        response = authenticated_client.get("/me/categories/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1


class TestCategoryUpdate:

    def test_update_category_persists_changes(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category,
        test_db: Session
    ):
        response = authenticated_client.put(
            f"/me/categories/{test_custom_category.category_id}",
            json={"name": "Updated Name", "tag": "Red"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "updated name"
        assert data["tag"] == "Red"
        
        test_db.refresh(test_custom_category)
        assert test_custom_category.name == "updated name"
        assert test_custom_category.tag == "Red"


class TestCategoryDeletion:

    def test_delete_category_removes_from_database(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category,
        test_db: Session
    ):
        category_id = test_custom_category.category_id
        
        response = authenticated_client.delete(f"/me/categories/{category_id}")
        
        assert response.status_code == 200
        
        deleted = test_db.get(Category, category_id)
        assert deleted is None


class TestCategoryExpenses:

    def test_get_category_expenses(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_expense: Expense
    ):
        response = authenticated_client.get(
            f"/me/categories/{test_category.category_id}/expenses"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        expense_ids = [exp["expense_id"] for exp in data]
        assert test_expense.expense_id in expense_ids

