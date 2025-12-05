"""
Unit tests for Pydantic model validation.

SCOPE: Tests validation rules BEFORE data hits the service layer.
- Pydantic field constraints (length, regex, type, enum)
- Whitespace/case normalization

NOT IN SCOPE:
- Database uniqueness (see test_db_constraints.py)
- Service layer business logic (see test_*_service.py)
- Authorization (403 - see test_cross_user_security.py)
"""
import pytest
from pydantic import ValidationError

from app.models import UserCreate, CategoryCreate, ExpenseCreate
from app.models.category import Color


# ============================================================================
# PYDANTIC FIELD VALIDATION (No DB)
# ============================================================================

class TestUserFieldConstraints:
    """
    UserCreate Pydantic validation.
    Tests: length limits, regex patterns, type constraints.
    Expects: ValidationError on invalid input.
    """

    @pytest.mark.parametrize("username,error_type", [
        ("ab", "string_too_short"),           # 2 < min 3
        ("a" * 51, "string_too_long"),        # 51 > max 50
        ("user name", "string_pattern"),      # space violates ^[a-zA-Z0-9_-]+$
        ("user@name!", "string_pattern"),     # @ and ! violate regex
        ("", "string_too_short"),             # empty -> too short after normalization
    ])
    def test_username_rejected(self, username, error_type):
        with pytest.raises(ValidationError) as exc:
            UserCreate(username=username, email="t@t.com", salary=0, password="validpass")
        assert error_type in str(exc.value)

    @pytest.mark.parametrize("username", ["abc", "a" * 50, "user_name-123"])
    def test_username_accepted_at_boundaries(self, username):
        user = UserCreate(username=username, email="t@t.com", salary=0, password="validpass")
        assert user.username == username.lower()  # normalized to lowercase

    @pytest.mark.parametrize("email", ["notanemail", "user@", "a" * 120 + "@test.com"])
    def test_email_rejected(self, email):
        with pytest.raises(ValidationError):
            UserCreate(username="validuser", email=email, salary=0, password="validpass")

    @pytest.mark.parametrize("password,error_type", [
        ("short", "string_too_short"),        # 5 < min 8
        ("a" * 129, "string_too_long"),       # 129 > max 128
    ])
    def test_password_rejected(self, password, error_type):
        with pytest.raises(ValidationError) as exc:
            UserCreate(username="validuser", email="t@t.com", salary=0, password=password)
        assert error_type in str(exc.value)

    def test_salary_negative_rejected(self):
        with pytest.raises(ValidationError) as exc:
            UserCreate(username="validuser", email="t@t.com", salary=-1, password="validpass")
        assert "greater_than_equal" in str(exc.value)

    def test_salary_zero_and_null_accepted(self):
        assert UserCreate(username="user1", email="a@b.com", salary=0, password="validpass").salary == 0
        assert UserCreate(username="user2", email="c@d.com", salary=None, password="validpass").salary is None


class TestCategoryFieldConstraints:
    """
    CategoryCreate Pydantic validation.
    Tests: SmallText (1-50), LongText (1-1000), Color enum.
    Expects: ValidationError on invalid input.
    """

    @pytest.mark.parametrize("name", ["", "a" * 51, "   "])
    def test_name_rejected(self, name):
        with pytest.raises(ValidationError):
            CategoryCreate(name=name)

    @pytest.mark.parametrize("name", ["X", "a" * 50])
    def test_name_accepted_at_boundaries(self, name):
        cat = CategoryCreate(name=name)
        assert cat.name == name.lower()  # normalized to lowercase

    @pytest.mark.parametrize("description", ["", "a" * 1001, "   "])
    def test_description_rejected_when_provided(self, description):
        with pytest.raises(ValidationError):
            CategoryCreate(name="Valid", description=description)

    def test_description_null_accepted(self):
        assert CategoryCreate(name="Valid", description=None).description is None

    @pytest.mark.parametrize("tag", ["InvalidColor", "blue", "BLUE"])
    def test_tag_invalid_enum_rejected(self, tag):
        with pytest.raises(ValidationError):
            CategoryCreate(name="Valid", tag=tag)

    def test_tag_valid_enum_accepted(self):
        for color in Color:
            assert CategoryCreate(name=f"C{color.value}", tag=color).tag == color


class TestExpenseFieldConstraints:
    """
    ExpenseCreate Pydantic validation.
    Tests: SmallText name, PositiveAmount, LongText description.
    Expects: ValidationError on invalid input.
    """

    @pytest.mark.parametrize("name", ["", "a" * 51, "   "])
    def test_name_rejected(self, name):
        with pytest.raises(ValidationError):
            ExpenseCreate(name=name, amount=100)

    def test_amount_negative_rejected(self):
        with pytest.raises(ValidationError) as exc:
            ExpenseCreate(name="Valid", amount=-1)
        assert "greater_than_equal" in str(exc.value)

    def test_amount_zero_accepted(self):
        assert ExpenseCreate(name="Valid", amount=0).amount == 0

    @pytest.mark.parametrize("description", ["", "a" * 1001])
    def test_description_rejected_when_provided(self, description):
        with pytest.raises(ValidationError):
            ExpenseCreate(name="Valid", amount=100, description=description)


# ============================================================================
# INPUT NORMALIZATION (No DB)
# ============================================================================

class TestInputNormalization:
    """
    Whitespace trimming and case normalization.
    Tests: strip(), lower() applied before validation.
    Expects: Normalized values stored in model.
    """

    def test_user_whitespace_trimmed_and_lowercased(self):
        user = UserCreate(username="  TestUser  ", email="  Test@Example.COM  ", salary=0, password="validpass")
        assert user.username == "testuser"
        assert user.email == "test@example.com"

    def test_user_whitespace_only_rejected(self):
        with pytest.raises(ValidationError):
            UserCreate(username="   ", email="t@t.com", salary=0, password="validpass")

    def test_category_name_whitespace_trimmed_and_lowercased(self):
        cat = CategoryCreate(name="  Food  ")
        assert cat.name == "food"  # lowercased


