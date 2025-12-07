"""
Integration tests for expense endpoints (/me/expenses).

These tests verify:
- Expense CRUD operations via HTTP
- Expense listing with pagination
- Category-expense relationship handling

NOTE: Multi-user isolation (403) tests are in unit/test_cross_user_security.py
NOTE: Cascade delete tests are in unit/test_category_service.py
"""
from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import Expense, Category
from datetime import date


class TestExpenseCreation:

    def test_create_expense_persists_to_database(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_user,
        test_db: Session
    ):
        response = authenticated_client.post("/me/expenses/", json={
            "name": "Dinner",
            "amount": 45.50,
            "category_id": test_category.category_id
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Dinner"
        assert data["amount"] == 45.50
        assert data["category_id"] == test_category.category_id
        assert "expense_id" in data
        
        expense = test_db.get(Expense, data["expense_id"])
        assert expense is not None
        assert expense.name == "Dinner"
        assert expense.user_id == test_user.user_id

    def test_create_expense_with_nonexistent_category_fails(
        self,
        authenticated_client: TestClient
    ):
        response = authenticated_client.post("/me/expenses/", json={
            "name": "Test",
            "amount": 10.0,
            "category_id": 99999
        })
        
        assert response.status_code == 404


class TestExpenseRetrieval:

    def test_get_expense_by_id(
        self,
        authenticated_client: TestClient,
        test_expense: Expense
    ):
        response = authenticated_client.get(
            f"/me/expenses/{test_expense.expense_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["expense_id"] == test_expense.expense_id
        assert data["name"] == test_expense.name
        assert data["amount"] == test_expense.amount

    def test_get_nonexistent_expense_fails(self, authenticated_client: TestClient):
        response = authenticated_client.get("/me/expenses/99999")
        
        assert response.status_code == 404


class TestExpenseListing:

    def test_list_expenses_default_pagination(
        self,
        authenticated_client: TestClient,
        test_expense: Expense
    ):
        response = authenticated_client.get("/me/expenses/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        expense_ids = [exp["expense_id"] for exp in data]
        assert test_expense.expense_id in expense_ids

    def test_list_expenses_with_limit(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_db: Session,
        test_category: Category,
        test_user
    ):
        extra_expense = Expense(
            name="Extra",
            amount=20.0,
            category_id=test_category.category_id, #type: ignore
            user_id=test_user.user_id,
            date_of_entry=date.today()
        )
        test_db.add(extra_expense)
        test_db.commit()
        
        response = authenticated_client.get("/me/expenses/?limit=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1

    def test_list_expenses_with_offset(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_db: Session,
        test_category: Category,
        test_user
    ):
        extra_expense = Expense(
            name="Extra Offset",
            amount=20.0,
            category_id=test_category.category_id, #type: ignore
            user_id=test_user.user_id,
            date_of_entry=date.today()
        )
        test_db.add(extra_expense)
        test_db.commit()
        
        response_all = authenticated_client.get("/me/expenses/")
        total_count = len(response_all.json())
        
        response = authenticated_client.get("/me/expenses/?offset=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == total_count - 1


class TestExpenseUpdate:

    def test_update_expense_persists_changes(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_db: Session
    ):
        response = authenticated_client.put(
            f"/me/expenses/{test_expense.expense_id}",
            json={
                "name": "Updated Expense",
                "amount": 99.99
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["name"] == "Updated Expense"
        assert data["amount"] == 99.99
        
        test_db.refresh(test_expense)
        assert test_expense.name == "Updated Expense"
        assert test_expense.amount == 99.99

    def test_update_expense_change_category(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_custom_category: Category,
        test_db: Session
    ):
        response = authenticated_client.put(
            f"/me/expenses/{test_expense.expense_id}",
            json={"category_id": test_custom_category.category_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category_id"] == test_custom_category.category_id
        
        test_db.refresh(test_expense)
        assert test_expense.category_id == test_custom_category.category_id


class TestExpenseDeletion:

    def test_delete_expense_removes_from_database(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_db: Session
    ):
        expense_id = test_expense.expense_id
        
        response = authenticated_client.delete(f"/me/expenses/{expense_id}")
        
        assert response.status_code == 200
        
        deleted = test_db.get(Expense, expense_id)
        assert deleted is None


class TestExpenseCategoryRelationship:

    def test_expense_references_correct_category(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_category: Category
    ):
        """Expense correctly references its category"""
        response = authenticated_client.get(
            f"/me/expenses/{test_expense.expense_id}"
        )
        
        data = response.json()
        assert data["category_id"] == test_category.category_id

