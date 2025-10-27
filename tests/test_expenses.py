from fastapi.testclient import TestClient
from app.main import app
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

