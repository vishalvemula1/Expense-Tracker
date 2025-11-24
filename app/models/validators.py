from datetime import date
from typing import Annotated
from sqlmodel import Field
from pydantic import StringConstraints, field_validator

PositiveAmount = Annotated[float, 
                           Field(ge=0, 
                                 description="Amount must be greater than or equal to zero"
                            )]


DateCheck = Annotated[date, Field(default_factory=date.today)]
"""Date fields that defaults to today's date. Used for a class' entry and update to record time of entry"""

SmallText = Annotated[str, StringConstraints(min_length=1, max_length=50, strip_whitespace=True)]

LongText = Annotated[str, StringConstraints(min_length=1, max_length=1000, strip_whitespace=True)]


def create_string_validators(*field_names):
    """
    Creates a validator mixin that trims whitespace and rejects empty strings.
    
    Args:
        *fields: Field names to validate (e.g., 'username', 'email')
    
    Returns:
        StringValidatorsMixin class to use as a base class
    
    Example:
        Validator = create_string_validators('username', 'email')
        class User(BaseModel, Validator):
            username: str
            email: str
    """
    if not field_names:
        raise ValueError("At least one field must be specified")

    class WhitespaceTrimmerMixin:
        """Validates string fields by trimming whitespace and rejecting empty values"""

        @field_validator(*field_names, mode="before")
        @classmethod
        def validate_string_fields(cls, value, info):
            if value is None:
                return value

            if not isinstance(value, str):
                return value

            value = value.strip()

            if value == "":
                raise ValueError(f"{info.field_name} cannot be empty or whitespace only")

            return value

    return WhitespaceTrimmerMixin