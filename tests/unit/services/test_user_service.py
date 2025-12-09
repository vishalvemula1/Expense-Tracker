"""
UserService Unit Tests

Tests for user service internals:
- Password update hashing
- Partial update field preservation
- Uniqueness on update (409)
- Self-update edge cases
- Cascade delete verification
"""
import pytest
from sqlmodel import Session, select
from fastapi import HTTPException

from app.models import User, UserCreate, UserUpdate, Category, Expense, CategoryCreate, ExpenseCreate
from app.models.category_models import Color
from app.services import AuthService, UserService, CategoryService, ExpenseService


class TestPasswordUpdate:

    def test_password_update_is_hashed(self, test_db: Session, test_user: User):
        old_hash = test_user.password_hash
        svc = UserService(test_user, test_db)
        
        svc.update(UserUpdate(password="newpassword123"))
        
        assert test_user.password_hash != old_hash
        assert test_user.password_hash != "newpassword123"


class TestPartialUpdate:

    def test_partial_update_preserves_salary(self, test_db: Session, test_user: User):
        original_salary = test_user.salary
        svc = UserService(test_user, test_db)
        
        svc.update(UserUpdate(username="newname"))
        
        test_db.refresh(test_user)
        assert test_user.salary == original_salary

    def test_empty_update_changes_nothing(self, test_db: Session, test_user: User):
        original = (test_user.username, test_user.email, test_user.salary)
        svc = UserService(test_user, test_db)
        
        svc.update(UserUpdate())
        
        test_db.refresh(test_user)
        assert (test_user.username, test_user.email, test_user.salary) == original


class TestUniquenessOnUpdate:

    @pytest.mark.parametrize("field,get_value,expected_detail", [
        pytest.param("username", lambda u: u.username, "Username", id="username"),
        pytest.param("email", lambda u: u.email, "Email", id="email"),
    ])
    def test_update_to_existing_value_fails(
        self, test_db: Session, test_user: User, other_user: User, field, get_value, expected_detail
    ):
        svc = UserService(test_user, test_db)
        
        with pytest.raises(HTTPException) as exc:
            svc.update(UserUpdate(**{field: get_value(other_user)}))
        
        assert exc.value.status_code == 409
        assert expected_detail in exc.value.detail

    @pytest.mark.parametrize("field,get_value", [
        pytest.param("username", lambda u: u.username, id="username"),
        pytest.param("email", lambda u: u.email, id="email"),
    ])
    def test_update_to_own_value_succeeds(self, test_db: Session, test_user: User, field, get_value):
        svc = UserService(test_user, test_db)
        original_value = get_value(test_user)
        
        svc.update(UserUpdate(**{field: original_value}))
        
        test_db.refresh(test_user)
        assert get_value(test_user) == original_value


class TestCascadeDelete:

    def test_delete_cascades_to_categories_and_expenses(self, test_db: Session):
        auth = AuthService(test_db)
        user = auth.create_user_with_defaults(
            UserCreate(username="cascadeuser", email="cascade@test.com", salary=0, password="pass1234")
        )
        user_id = user.user_id
        
        cat_svc = CategoryService(user, test_db)
        category = cat_svc.create(CategoryCreate(name="Custom", tag=Color.Blue))
        
        exp_svc = ExpenseService(user, test_db)
        exp_svc.create(ExpenseCreate(name="Expense1", amount=100, category_id=category.category_id))
        
        UserService(user, test_db).delete()
        
        categories = test_db.exec(select(Category).where(Category.user_id == user_id)).all()
        expenses = test_db.exec(select(Expense).where(Expense.user_id == user_id)).all()
        
        assert len(categories) == 0
        assert len(expenses) == 0
