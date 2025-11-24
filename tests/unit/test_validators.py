import pytest
from app.models import UserCreate, CategoryCreate, ExpenseCreate, ExpenseUpdate, UserUpdate, CategoryUpdate


class TestStrictValidator:
    """Tests for 'strict' whitespace strategy - removes ALL whitespace"""

    def test_strict_removes_leading_trailing_whitespace(self):
        """Strict validator removes leading and trailing whitespace"""
        user = UserCreate(
            username="  trimme  ",
            email="test@example.com",
            password="  pass  ",
            salary=1000
        )
        
        assert user.username == "trimme"
        assert user.password == "pass"

    def test_strict_removes_all_internal_whitespace(self):
        """Strict validator removes all whitespace between words"""
        user = UserCreate(
            username="hello world test",
            email="test@example.com",
            password=" pass word ",  # Password uses 'trimmed', keeps internal spaces
            salary=1000
        )
        
        assert user.username == "helloworldtest"
        assert user.password == "pass word"  # Trimmed preserves internal whitespace

    def test_strict_rejects_empty_string(self):
        """Strict validator rejects empty strings"""
        with pytest.raises(ValueError, match="username cannot be empty"):
            UserCreate(
                username="",
                email="test@example.com",
                password="pass",
                salary=1000
            )

    def test_strict_rejects_whitespace_only(self):
        """Strict validator rejects whitespace-only strings"""
        with pytest.raises(ValueError, match="username cannot be empty"):
            UserCreate(
                username="   ",
                email="test@example.com",
                password="pass",
                salary=1000
            )

    def test_strict_rejects_password_whitespace_only(self):
        """Strict validator rejects whitespace-only password"""
        with pytest.raises(ValueError, match="password cannot be empty"):
            UserCreate(
                username="user",
                email="test@example.com",
                password="   ",
                salary=1000
            )


class TestTrimmedValidator:
    """Tests for 'trimmed' whitespace strategy - only removes leading/trailing"""

    def test_trimmed_preserves_internal_whitespace(self):
        """Trimmed validator preserves spaces between words"""
        category = CategoryCreate(
            name="Food and Drink",
            description="All food and drink expenses",
            tag="Blue"
        )
        
        assert category.name == "Food and Drink"
        assert category.description == "All food and drink expenses"

    def test_trimmed_removes_leading_trailing(self):
        """Trimmed validator removes leading and trailing whitespace"""
        expense = ExpenseCreate(
            name="  Groceries  ",
            amount=50.0,
            description="  Weekly shopping  "
        )
        
        assert expense.name == "Groceries"
        assert expense.description == "Weekly shopping"

    def test_trimmed_rejects_empty_string(self):
        """Trimmed validator rejects empty strings"""
        with pytest.raises(ValueError, match="name cannot be empty"):
            CategoryCreate(
                name="",
                tag="Blue"
            )

    def test_trimmed_rejects_whitespace_only(self):
        """Trimmed validator rejects whitespace-only strings"""
        with pytest.raises(ValueError, match="name cannot be empty"):
            CategoryCreate(
                name="   ",
                tag="Blue"
            )


class TestValidatorOnUpdate:
    """Tests that validators work on Update models too"""

    def test_user_update_validates_username(self):
        """UserUpdate applies strict validation to username"""
        update = UserUpdate(username="hello world")
        assert update.username == "helloworld"

    def test_user_update_rejects_empty_username(self):
        """UserUpdate rejects empty username"""
        with pytest.raises(ValueError, match="username cannot be empty"):
            UserUpdate(username="   ")

    def test_category_update_validates_name(self):
        """CategoryUpdate applies trimmed validation to name"""
        update = CategoryUpdate(name="  Food and Drink  ")
        assert update.name == "Food and Drink"

    def test_expense_update_rejects_empty_name(self):
        """ExpenseUpdate rejects empty name"""
        with pytest.raises(ValueError, match="name cannot be empty"):
            ExpenseUpdate(name="")


class TestValidatorWithNone:
    """Tests that validators handle None values correctly"""

    def test_optional_fields_accept_none(self):
        """Optional fields accept None without validation"""
        update = UserUpdate(
            username=None,
            email=None,
            password=None,
            salary=None
        )
        
        assert update.username is None
        assert update.email is None
        assert update.password is None

    def test_optional_description_accepts_none(self):
        """Optional description accepts None"""
        category = CategoryCreate(
            name="Food",
            description=None,
            tag="Blue"
        )
        
        assert category.description is None
