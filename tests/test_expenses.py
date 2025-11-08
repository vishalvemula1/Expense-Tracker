from fastapi.testclient import TestClient
from app.models import User, Expense
from sqlmodel import Session

# ====================================================================
# Testing for the read expense (get) endpoint in expenses.py
# ====================================================================
def test_read_expense_happy_path(test_expense: Expense, test_user: User, authenticated_client: TestClient):
    response = authenticated_client.get(
        f"/me/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_expense.name

def test_read_expense_nonexistant_expense(test_expense: Expense, 
                                          authenticated_client: TestClient, 
                                          test_user: User):
    response = authenticated_client.get(
        f"/me/expenses/{2}"
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Expense was not found"

def test_read_expense_unauthenticated(test_expense: Expense, test_user: User, client: TestClient):
    response = client.get(
        f"/me/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# ====================================================================
# Testing for the add expense (post) endpoint in expenses.py
# ====================================================================

def test_add_expense_happy_path(authenticated_client: TestClient, test_user: User, test_category):
    response = authenticated_client.post(
        "/me/expenses/", json={
            "name": "Cheese",
            "amount": 50,
            "description": "Unforunate lack of judgement"
        }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Cheese"
    assert data["amount"] == 50
    assert data["user_id"] == test_user.user_id
    assert data["category_id"] == test_category.category_id  # Should use default category

def test_add_expense_not_authenticated(client: TestClient, test_user: User, test_category):
    response = client.post(
        "/me/expenses/", json={
            "name": "Cheese",
            "amount": 50,
            "description": "Unforunate lack of judgement"
        }
        )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_add_expense_invalid_data(authenticated_client: TestClient, test_user: User, test_category):
    response = authenticated_client.post(
        "/me/expenses/", json={
            "name": "",
            "amount": -50,
            "description": "Unforunate lack of judgement"
        }
        )

    assert response.status_code == 422

def test_add_expense_with_category_id(authenticated_client: TestClient, test_user: User, test_new_category):
    response = authenticated_client.post(
        "/me/expenses/", json={
            "name": "Laptop",
            "amount": 1200,
            "category_id": test_new_category.category_id,
            "description": "Work laptop"
        }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Laptop"
    assert data["category_id"] == test_new_category.category_id

def test_add_expense_without_category_id(authenticated_client: TestClient, test_user: User, test_category):
    response = authenticated_client.post(
        "/me/expenses/", json={
            "name": "Coffee",
            "amount": 5.50
        }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Coffee"
    assert data["category_id"] == test_category.category_id  # Should use default

def test_add_expense_with_invalid_category_id(authenticated_client: TestClient, test_user: User, test_category):
    response = authenticated_client.post(
        "/me/expenses/", json={
            "name": "Invalid",
            "amount": 100,
            "category_id": 9999
        }
        )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Category was not found"

def test_add_expense_with_other_users_category(authenticated_client: TestClient, test_user: User, test_db):
    from app.auth import get_password_hash
    from app.models import Category
    from datetime import date

    # Create another user with their own category
    hashed_pw = get_password_hash("password")
    other_user = User(
        username="otheruser",
        email="other@example.com",
        password_hash=hashed_pw,
        salary=50000
    )
    test_db.add(other_user)
    test_db.commit()
    test_db.refresh(other_user)

    assert other_user.user_id is not None

    other_category = Category(
        name="OtherCategory",
        user_id=other_user.user_id,
        date_of_entry=date.today()
    )
    test_db.add(other_category)
    test_db.commit()
    test_db.refresh(other_category)

    # Try to use other user's category
    response = authenticated_client.post(
        "/me/expenses/", json={
            "name": "Unauthorized",
            "amount": 100,
            "category_id": other_category.category_id
        }
        )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

# ====================================================================
# Testing for the read all expenses (get) endpoint in expenses.py
# ====================================================================



def test_read_all_expenses_happy_path(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.get("/me/expenses/")

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == "Test Expense"

def test_read_all_expenses_unauthenticated(client: TestClient, test_user: User, test_expense: Expense):
    response = client.get("/me/expenses/")

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# ====================================================================
# Testing for the delete expense (delete) endpoint in expenses.py
# ====================================================================

def test_delete_expense_happy_path(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.delete(
        f"/me/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["expense_id"] == test_expense.expense_id

def test_delete_expense_unauthenticated(client: TestClient, test_user: User, test_expense: Expense):
    response = client.delete(
        f"/me/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_delete_expense_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.delete(
        "/me/expenses/999"
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Expense was not found"

# ====================================================================
# Testing for the update expense (put) endpoint in expenses.py
# ====================================================================

def test_update_expense_happy_path(authenticated_client: TestClient, test_user: User, test_expense: Expense, test_new_category):
    response = authenticated_client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "name": "Updated Expense",
            "amount": 200.0,
            "category_id": test_new_category.category_id,
            "description": "Updated description"
        }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Expense"
    assert data["amount"] == 200.0
    assert data["category_id"] == test_new_category.category_id

def test_update_expense_partial(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "name": "Partially Updated"
        }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Partially Updated"
    assert data["amount"] == test_expense.amount  # Original amount preserved

def test_update_expense_unauthenticated(client: TestClient, test_user: User, test_expense: Expense):
    response = client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "name": "Updated"
        }
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_update_expense_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.put(
        "/me/expenses/999", json={
            "name": "Updated"
        }
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Expense was not found"

def test_update_expense_invalid_data(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "name": "",
            "amount": -50
        }
        )

    assert response.status_code == 422

def test_update_expense_change_category(authenticated_client: TestClient, test_user: User, test_expense: Expense, test_new_category):
    response = authenticated_client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "category_id": test_new_category.category_id
        }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["category_id"] == test_new_category.category_id
    assert data["name"] == test_expense.name  # Other fields unchanged

def test_update_expense_to_default_category(authenticated_client: TestClient, test_user: User, test_expense: Expense, test_category):
    response = authenticated_client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "name": "Updated Name"
        }
        )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Name"
    # Category should remain the same if not specified
    assert data["category_id"] == test_expense.category_id

def test_update_expense_with_invalid_category(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/me/expenses/{test_expense.expense_id}", json={
            "category_id": 9999
        }
        )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Category was not found"

def test_update_expense_with_other_users_category(user1_client: TestClient, multi_user_data):
    from tests.conftest import MultiUserData
    data: MultiUserData = multi_user_data

    # SECURITY TEST: User1 tries to update their expense to use User2's category
    response = user1_client.put(
        f"/me/expenses/{data.user1_expenses[0].expense_id}",
        json={"category_id": data.user2_travel_category.category_id}
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Not authorized for this request"

def test_add_expense_without_category_uses_correct_default(user1_client: TestClient, multi_user_data):
    from tests.conftest import MultiUserData
    data: MultiUserData = multi_user_data

    # SECURITY TEST: User1 creates expense without category - should use their own default
    response = user1_client.post(
        "/me/expenses/",
        json={"name": "Test Expense", "amount": 100.0}
    )

    assert response.status_code == 200
    result = response.json()
    assert result["category_id"] == data.user1_default_category.category_id
    assert result["category_id"] != data.user2_default_category.category_id
