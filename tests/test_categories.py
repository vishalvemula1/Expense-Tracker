from fastapi.testclient import TestClient
from sqlmodel import Session
from app.models import User, Category, Expense

# ====================================================================
# Testing for the create category (post) endpoint in categories.py
# ====================================================================

def test_create_category_happy_path(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.post(
        "/me/categories/", json={
            "name": "Food",
            "description": "Food and groceries",
            "tag": "Blue"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Food"
    assert data["description"] == "Food and groceries"
    assert data["tag"] == "Blue"
    assert data["is_default"] == False

def test_create_category_minimal_fields(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.post(
        "/me/categories/", json={
            "name": "Travel"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Travel"
    assert data["description"] is None
    assert data["tag"] is None

def test_create_category_duplicate_name_same_user(authenticated_client: TestClient, test_user: User, test_category):
    response = authenticated_client.post(
        "/me/categories/", json={
            "name": "Uncategorized"
        }
    )

    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Category with the same name already exists"

def test_create_category_duplicate_name_different_user(user2_client: TestClient, multi_user_data):
    # user1 already has "Food" category, user2 should be able to create their own "Food"
    response = user2_client.post(
        "/me/categories/", json={
            "name": "Food",
            "description": "My food category"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Food"

def test_create_category_unauthenticated(client: TestClient, test_user: User):
    response = client.post(
        "/me/categories/", json={
            "name": "Food"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_create_category_empty_name(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.post(
        "/me/categories/", json={
            "name": ""
        }
    )

    assert response.status_code == 422
    data = response.json()
    assert "name cannot be empty or whitespace only" in data["detail"][0]["msg"]

def test_create_category_whitespace_name(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.post(
        "/me/categories/", json={
            "name": "   "
        }
    )

    assert response.status_code == 422

# ====================================================================
# Testing for the read category (get) endpoint in categories.py
# ====================================================================

def test_read_category_happy_path(authenticated_client: TestClient, test_user: User, test_category: Category):
    response = authenticated_client.get(
        f"/me/categories/{test_category.category_id}"
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_category.name
    assert data["category_id"] == test_category.category_id

def test_read_category_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.get(
        "/me/categories/9999"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Category was not found"

def test_read_category_unauthenticated(client: TestClient, test_user: User, test_category: Category):
    response = client.get(
        f"/me/categories/{test_category.category_id}"
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

# ====================================================================
# Testing for the read all categories (get) endpoint in categories.py
# ====================================================================

def test_read_all_categories_happy_path(authenticated_client: TestClient, test_user: User, test_category: Category):
    response = authenticated_client.get(
        "/me/categories/"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(cat["name"] == "Uncategorized" for cat in data)

def test_read_all_categories_includes_default(authenticated_client: TestClient, test_user: User, test_category: Category):
    response = authenticated_client.get(
        "/me/categories/"
    )

    assert response.status_code == 200
    data = response.json()

    # Find default category
    default_cats = [cat for cat in data if cat["is_default"]]
    assert len(default_cats) == 1
    assert default_cats[0]["name"] == "Uncategorized"

def test_read_all_categories_multiple(authenticated_client: TestClient, test_user: User, test_category: Category, test_new_category: Category):
    response = authenticated_client.get(
        "/me/categories/"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2
    category_names = [cat["name"] for cat in data]
    assert "Uncategorized" in category_names
    assert "First Category" in category_names

def test_read_all_categories_unauthenticated(client: TestClient, test_user: User):
    response = client.get(
        "/me/categories/"
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_read_all_categories_pagination(authenticated_client: TestClient, test_user: User, test_category: Category, test_db: Session):
    from datetime import date

    # Create multiple categories
    assert test_user.user_id is not None
    for i in range(10):
        cat = Category(
            name=f"Category{i}",
            user_id=test_user.user_id,
            date_of_entry=date.today()
        )
        test_db.add(cat)
    test_db.commit()

    # Test with limit
    response = authenticated_client.get(
        "/me/categories/?limit=5"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

    # Test with offset
    response = authenticated_client.get(
        "/me/categories/?limit=5&offset=5"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5

# ====================================================================
# Testing for the update category (put) endpoint in categories.py
# ====================================================================

def test_update_category_happy_path(authenticated_client: TestClient, test_user: User, test_new_category: Category):
    response = authenticated_client.put(
        f"/me/categories/{test_new_category.category_id}", json={
            "name": "Updated Category",
            "description": "Updated description",
            "tag": "Red"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["description"] == "Updated description"
    assert data["tag"] == "Red"

def test_update_category_partial(authenticated_client: TestClient, test_user: User, test_new_category: Category):
    original_name = test_new_category.name

    response = authenticated_client.put(
        f"/me/categories/{test_new_category.category_id}", json={
            "description": "Only updating description"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Only updating description"
    # Name should remain unchanged
    assert data["name"] == original_name

def test_update_category_cannot_edit_default(authenticated_client: TestClient, test_user: User, test_category: Category):
    response = authenticated_client.put(
        f"/me/categories/{test_category.category_id}", json={
            "name": "Trying to change default"
        }
    )

    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Not allowed to edit or delete default category"

def test_update_category_duplicate_name(authenticated_client: TestClient, test_user: User, test_category: Category, test_new_category: Category):
    # Try to rename test_new_category to "Uncategorized" (which already exists)
    response = authenticated_client.put(
        f"/me/categories/{test_new_category.category_id}", json={
            "name": "Uncategorized"
        }
    )

    assert response.status_code == 409
    data = response.json()
    assert data["detail"] == "Category with the same name already exists"

def test_update_category_unauthenticated(client: TestClient, test_user: User, test_new_category: Category):
    response = client.put(
        f"/me/categories/{test_new_category.category_id}", json={
            "name": "Updated"
        }
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_update_category_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.put(
        "/me/categories/9999", json={
            "name": "Updated"
        }
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Category was not found"

def test_update_category_empty_name(authenticated_client: TestClient, test_user: User, test_new_category: Category):
    response = authenticated_client.put(
        f"/me/categories/{test_new_category.category_id}", json={
            "name": ""
        }
    )

    assert response.status_code == 422

# ====================================================================
# Testing for the delete category (delete) endpoint in categories.py
# ====================================================================

def test_delete_category_happy_path(authenticated_client: TestClient, test_user: User, test_new_category: Category):
    response = authenticated_client.delete(
        f"/me/categories/{test_new_category.category_id}"
    )

    assert response.status_code == 200

    # Verify it's deleted
    response = authenticated_client.get(
        f"/me/categories/{test_new_category.category_id}"
    )
    assert response.status_code == 404

def test_delete_category_unauthenticated(client: TestClient, test_user: User, test_new_category: Category):
    response = client.delete(
        f"/me/categories/{test_new_category.category_id}"
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_delete_category_nonexistent(authenticated_client: TestClient, test_user: User):
    response = authenticated_client.delete(
        "/me/categories/9999"
    )

    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Category was not found"

def test_delete_default_category_should_fail(authenticated_client: TestClient, test_user: User, test_category: Category):
    response = authenticated_client.delete(
        f"/me/categories/{test_category.category_id}"
    )

    assert response.status_code in [403, 409]
    data = response.json()
    assert "default" in data["detail"].lower()

# ====================================================================
# Testing for the get expenses by category endpoint in categories.py
# ====================================================================

def test_get_expenses_by_category_happy_path(authenticated_client: TestClient, test_user: User, test_category: Category, test_expense: Expense):
    response = authenticated_client.get(
        f"/me/categories/{test_category.category_id}/expenses"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["name"] == test_expense.name
    assert data[0]["category_id"] == test_category.category_id

def test_get_expenses_by_default_category(authenticated_client: TestClient, test_user: User, test_category: Category, test_expense: Expense):
    # test_expense should be in the default category
    response = authenticated_client.get(
        f"/me/categories/{test_category.category_id}/expenses"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    expense_ids = [exp["expense_id"] for exp in data]
    assert test_expense.expense_id in expense_ids

def test_get_expenses_by_category_empty(authenticated_client: TestClient, test_user: User, test_new_category: Category):
    # test_new_category has no expenses
    response = authenticated_client.get(
        f"/me/categories/{test_new_category.category_id}/expenses"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0

def test_get_expenses_by_category_multiple(authenticated_client: TestClient, test_user: User, test_category: Category, test_db: Session):
    from datetime import date

    assert test_user.user_id is not None
    assert test_category.category_id is not None

    # Create multiple expenses in the same category
    for i in range(3):
        expense = Expense(
            name=f"Expense{i}",
            amount=100.0 + i,
            category_id=test_category.category_id,
            user_id=test_user.user_id,
            date_of_entry=date.today()
        )
        test_db.add(expense)
    test_db.commit()

    response = authenticated_client.get(
        f"/me/categories/{test_category.category_id}/expenses"
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 3

def test_get_expenses_by_category_unauthenticated(client: TestClient, test_user: User, test_category: Category):
    response = client.get(
        f"/me/categories/{test_category.category_id}/expenses"
    )

    assert response.status_code == 401
    data = response.json()
    assert data["detail"] == "Not authenticated"

def test_get_expenses_by_category_unauthorized(user1_client: TestClient, multi_user_data):
    # user1 tries to access user2's category expenses
    response = user1_client.get(
        f"/me/categories/{multi_user_data.user2_travel_category.category_id}/expenses"
    )

    assert response.status_code == 403
    data = response.json()
    assert data["detail"] == "Not authorized for this request"
