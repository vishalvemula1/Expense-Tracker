from pydantic import field_validator
from typing import Literal


# ==========================================
# Validator Function & Mixins
# ==========================================

WhitespaceStrategy = Literal["strict", "trimmed"]

def create_string_validators(**field_configs: WhitespaceStrategy):
    """
    Factory function to create a mixin with field-specific validation strategies.

    This function creates a reusable validator mixin that can handle multiple fields
    with different whitespace processing rules.

    Args:
        **field_configs: Keyword arguments where:
            - key = field name (e.g., "username", "description")
            - value = whitespace strategy:
                * 'strict': Removes ALL whitespace including spaces between words
                            Use for: usernames, emails, codes, IDs
                            Example: "hello world" -> "helloworld"

                * 'trimmed': Only removes leading/trailing whitespace, keeps internal spaces
                             Use for: descriptions, names, addresses, text content
                             Example: "  hello world  " -> "hello world"
    """

    if not field_configs:
        raise ValueError("At least one field must be specified")

    all_fields = tuple(field_configs.keys())

    class StringValidatorsMixin:
        """Validates string fields with configurable whitespace handling"""

        @field_validator(*all_fields, mode="before")
        @classmethod
        def validate_string_fields(cls, value, info):

            if value is None:
                return value

            if not isinstance(value, str):
                return value

            field_name = info.field_name

            strategy = field_configs.get(field_name)

            if strategy == "strict":
                value = "".join(value.split())

            elif strategy == "trimmed":
                value = value.strip()

            else:
                raise ValueError(f"Invalid strategy '{strategy}' for field '{field_name}'")

            if value == "":
                raise ValueError(f"{field_name} cannot be empty or whitespace only")

            return value

    return StringValidatorsMixin
