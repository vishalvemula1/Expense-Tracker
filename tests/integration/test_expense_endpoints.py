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
    """Test POST /me/expenses"""

    def test_create_expense_persists_to_database(
        self,
        authenticated_client: TestClient,
        test_category: Category,
        test_user,
        test_db: Session
    ):
        """Creating expense via API persists to database"""
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
        
        # Verify in database
        expense = test_db.get(Expense, data["expense_id"])
        assert expense is not None
        assert expense.name == "Dinner"
        assert expense.user_id == test_user.user_id

    def test_create_expense_with_nonexistent_category_fails(
        self,
        authenticated_client: TestClient
    ):
        """Creating expense with invalid category_id fails"""
        response = authenticated_client.post("/me/expenses/", json={
            "name": "Test",
            "amount": 10.0,
            "category_id": 99999  # Non-existent
        })
        
        assert response.status_code == 404


class TestExpenseRetrieval:
    """Test GET /me/expenses/{expense_id}"""

    def test_get_expense_by_id(
        self,
        authenticated_client: TestClient,
        test_expense: Expense
    ):
        """Can retrieve specific expense by ID"""
        response = authenticated_client.get(
            f"/me/expenses/{test_expense.expense_id}"
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["expense_id"] == test_expense.expense_id
        assert data["name"] == test_expense.name
        assert data["amount"] == test_expense.amount

    def test_get_nonexistent_expense_fails(self, authenticated_client: TestClient):
        """Getting non-existent expense returns 404"""
        response = authenticated_client.get("/me/expenses/99999")
        
        assert response.status_code == 404


class TestExpenseListing:
    """Test GET /me/expenses/ with pagination"""

    def test_list_expenses_default_pagination(
        self,
        authenticated_client: TestClient,
        test_expense: Expense
    ):
        """List expenses returns expenses for authenticated user"""
        response = authenticated_client.get("/me/expenses/")
        
        assert response.status_code == 200
        data = response.json()
        
        assert isinstance(data, list)
        assert len(data) >= 1
        
        # Verify expense in list
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
        """Limit parameter controls number of results"""
        # Create additional expense
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
        """Offset parameter skips results"""
        # Create additional expense
        extra_expense = Expense(
            name="Extra",
            amount=20.0,
            category_id=test_category.category_id, #type: ignore
            user_id=test_user.user_id,
            date_of_entry=date.today()
        )
        test_db.add(extra_expense)
        test_db.commit()
        
        # Get all expenses
        response_all = authenticated_client.get("/me/expenses/")
        total_count = len(response_all.json())
        
        # Get with offset
        response = authenticated_client.get("/me/expenses/?offset=1")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == total_count - 1


class TestExpenseUpdate:
    """Test PUT /me/expenses/{expense_id}"""

    def test_update_expense_persists_changes(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_db: Session
    ):
        """Updating expense via API persists changes"""
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
        
        # Verify in database
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
        """Can update expense to different category"""
        response = authenticated_client.put(
            f"/me/expenses/{test_expense.expense_id}",
            json={"category_id": test_custom_category.category_id}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["category_id"] == test_custom_category.category_id
        
        # Verify in database
        test_db.refresh(test_expense)
        assert test_expense.category_id == test_custom_category.category_id


class TestExpenseDeletion:
    """Test DELETE /me/expenses/{expense_id}"""

    def test_delete_expense_removes_from_database(
        self,
        authenticated_client: TestClient,
        test_expense: Expense,
        test_db: Session
    ):
        """Deleting expense removes it from database"""
        expense_id = test_expense.expense_id
        
        response = authenticated_client.delete(f"/me/expenses/{expense_id}")
        
        assert response.status_code == 200
        
        # Verify expense deleted
        deleted = test_db.get(Expense, expense_id)
        assert deleted is None


class TestExpenseCategoryRelationship:
    """Test that expense-category relationship is properly maintained"""

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

