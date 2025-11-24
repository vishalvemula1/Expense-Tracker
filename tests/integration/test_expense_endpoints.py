"""
Integration tests for expense endpoints (/me/expenses).

These tests verify:
- Expense CRUD operations via HTTP
- Expense listing with pagination
- Multi-user data isolation
- Category-expense relationship handling
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

    def test_create_expense_with_other_users_category_fails(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """Cannot create expense using another user's category"""
        user2_category_id = multi_user_data.user2_travel_category.category_id
        
        response = user1_client.post("/me/expenses/", json={
            "name": "Hack Attempt",
            "amount": 100.0,
            "category_id": user2_category_id  # User 2's category
        })
        
        assert response.status_code == 403


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


class TestMultiUserExpenseIsolation:
    """Test that users cannot access other users' expenses"""

    def test_user_cannot_view_other_users_expense(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """User 1 cannot access User 2's expense"""
        user2_expense_id = multi_user_data.user2_expenses[0].expense_id
        
        response = user1_client.get(f"/me/expenses/{user2_expense_id}")
        
        assert response.status_code == 403

    def test_user_cannot_update_other_users_expense(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """User 1 cannot update User 2's expense"""
        user2_expense_id = multi_user_data.user2_expenses[0].expense_id
        
        response = user1_client.put(
            f"/me/expenses/{user2_expense_id}",
            json={"name": "Hacked"}
        )
        
        assert response.status_code == 403

    def test_user_cannot_delete_other_users_expense(
        self,
        user1_client: TestClient,
        multi_user_data,
        test_db: Session
    ):
        """User 1 cannot delete User 2's expense"""
        user2_expense_id = multi_user_data.user2_expenses[0].expense_id
        
        response = user1_client.delete(f"/me/expenses/{user2_expense_id}")
        
        assert response.status_code == 403
        
        # Verify expense still exists
        expense = test_db.get(Expense, user2_expense_id)
        assert expense is not None

    def test_list_expenses_only_shows_own_expenses(
        self,
        user1_client: TestClient,
        multi_user_data
    ):
        """List endpoint only returns authenticated user's expenses"""
        response = user1_client.get("/me/expenses/")
        
        assert response.status_code == 200
        data = response.json()
        
        # Should have user1's expenses
        expense_names = [exp["name"] for exp in data]
        user1_expense_names = [exp.name for exp in multi_user_data.user1_expenses]
        for name in user1_expense_names:
            assert name in expense_names
        
        # Should NOT have user2's expenses
        user2_expense_names = [exp.name for exp in multi_user_data.user2_expenses]
        for name in user2_expense_names:
            assert name not in expense_names


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

    def test_category_deletion_affects_expenses(
        self,
        authenticated_client: TestClient,
        test_custom_category: Category,
        test_db: Session,
        test_user
    ):
        """When category is deleted, its expenses are handled appropriately"""
        # Create expense in custom category
        expense = Expense(
            name="Test",
            amount=50.0,
            category_id=test_custom_category.category_id, #type: ignore
            user_id=test_user.user_id,
            date_of_entry=date.today()
        )
        test_db.add(expense)
        test_db.commit()
        test_db.refresh(expense)
        expense_id = expense.expense_id
        
        # Delete the category
        authenticated_client.delete(
            f"/me/categories/{test_custom_category.category_id}"
        )
        
        # Expense should also be deleted (cascade)
        deleted_expense = test_db.get(Expense, expense_id)
        assert deleted_expense is None
