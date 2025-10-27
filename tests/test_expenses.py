from fastapi.testclient import TestClient
from app.models import User, Expense

# ====================================================================
# Testing for the read expense (get) endpoint in expenses.py
# ====================================================================
def test_read_expense_happy_path(test_expense: Expense, test_user: User, authenticated_client: TestClient):
    response = authenticated_client.get(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_expense.name

def test_read_expense_nonexistant_expense(test_expense: Expense, 
                                          authenticated_client: TestClient, 
                                          test_user: User):
    response = authenticated_client.get(
        f"/users/{test_user.user_id}/expenses/{2}"
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Expense was not found"

def test_read_expense_nonexistant_user(test_expense: Expense, 
                                         authenticated_client: TestClient):
    response = authenticated_client.get(
        f"/users/{3}/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

def test_read_expense_unauthenticated(test_expense: Expense, test_user: User, client: TestClient):
    response = client.get(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# ====================================================================
# Testing for the add expense (post) endpoint in expenses.py
# ====================================================================

def test_add_expense_happy_path(authenticated_client: TestClient, test_user: User, test_expense):
    response = authenticated_client.post(
        f"/users/{test_user.user_id}/expenses/", json={
            "name": "Cheese",
            "amount": 50,
            "category": "Food",
            "description": "Unforunate lack of judgement"
        }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["expense_id"] == 2
    assert data["user_id"] == 1

def test_add_expense_not_authenticated(client: TestClient, test_user: User, test_expense: Expense):
    response = client.post(
        f"/users/{test_user.user_id}/expenses/", json={
            "name": "Cheese",
            "amount": 50,
            "category": "Food",
            "description": "Unforunate lack of judgement"
        }
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_add_expense_unauthorized(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.post(
        f"/users/{3}/expenses/", json={
            "name": "Cheese",
            "amount": 50,
            "category": "Food",
            "description": "Unforunate lack of judgement"
        }
        )
    
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

def test_add_expense_invalid_data(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.post(
        f"/users/{test_user.user_id}/expenses/", json={
            "name": "",
            "amount": -50,
            "category": "Food",
            "description": "Unforunate lack of judgement"
        }
        )
    
    assert response.status_code == 422

# ====================================================================
# Testing for the read all expenses (get) endpoint in expenses.py
# ====================================================================



def test_read_all_expenses_happy_path(authenticated_client: TestClient, test_user: User, test_expense: Expense, create_test_expenses_and_users):
    response = authenticated_client.get(
        f"/users/{test_user.user_id}/expenses/"
        )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    assert data[1]["name"] == "Laptop"
    assert data[2]["name"] == "Wine"
    assert data[3]["name"] == "Rent"

def test_read_all_expenses_unauthenticated(client: TestClient, test_user: User, test_expense: Expense, create_test_expenses_and_users):
    response = client.get(
        f"/users/{test_user.user_id}/expenses/"
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_read_all_expenses_unauthorized(authenticated_client: TestClient, test_user: User, test_expense: Expense, create_test_expenses_and_users):
    response = authenticated_client.get(
        f"/users/{3}/expenses/"
        )
    
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

# ====================================================================
# Testing for the delete expense (delete) endpoint in expenses.py
# ====================================================================

def test_delete_expense_happy_path(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.delete(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["expense_id"] == test_expense.expense_id

def test_delete_expense_unauthenticated(client: TestClient, test_user: User, test_expense: Expense):
    response = client.delete(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_delete_expense_unauthorized(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.delete(
        f"/users/{3}/expenses/{test_expense.expense_id}"
        )
    
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

def test_delete_expense_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.delete(
        f"/users/{test_user.user_id}/expenses/{999}"
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Expense was not found"

# ====================================================================
# Testing for the update expense (put) endpoint in expenses.py
# ====================================================================

def test_update_expense_happy_path(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}", json={
            "name": "Updated Expense",
            "amount": 200.0,
            "category": "Updated Category",
            "description": "Updated description"
        }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Expense"
    assert data["amount"] == 200.0

def test_update_expense_partial(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}", json={
            "name": "Partially Updated"
        }
        )
    
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Partially Updated"
    assert data["amount"] == test_expense.amount  # Original amount preserved

def test_update_expense_unauthenticated(client: TestClient, test_user: User, test_expense: Expense):
    response = client.put(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}", json={
            "name": "Updated"
        }
        )
    
    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_update_expense_unauthorized(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/users/{3}/expenses/{test_expense.expense_id}", json={
            "name": "Updated"
        }
        )
    
    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"

def test_update_expense_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.put(
        f"/users/{test_user.user_id}/expenses/{999}", json={
            "name": "Updated"
        }
        )
    
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Expense was not found"

def test_update_expense_invalid_data(authenticated_client: TestClient, test_user: User, test_expense: Expense):
    response = authenticated_client.put(
        f"/users/{test_user.user_id}/expenses/{test_expense.expense_id}", json={
            "name": "",
            "amount": -50
        }
        )
    
    assert response.status_code == 422
