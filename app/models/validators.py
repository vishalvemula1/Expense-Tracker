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

    Returns:
        A mixin class that can be inherited by Pydantic models to validate the specified fields

    Raises:
        ValueError: If no fields are specified or if an invalid strategy is used

    Example:
        >>> # Create a validator for expense fields
        >>> ExpenseValidator = create_string_validators(
        ...     name="strict",        # No spaces allowed
        ...     description="trimmed"  # Internal spaces OK
        ... )
        >>>
        >>> # Use it in your model
        >>> class ExpenseCreate(ExpenseBase, ExpenseValidator):
        ...     pass
    """
    # Ensure at least one field was provided
    if not field_configs:
        raise ValueError("At least one field must be specified")

    # Extract all field names from the keyword arguments
    all_fields = tuple(field_configs.keys())

    class StringValidatorsMixin:
        """Validates string fields with configurable whitespace handling"""

        @field_validator(*all_fields, mode="before")
        @classmethod
        def validate_string_fields(cls, value, info):
            """
            Validates and processes string fields based on their configured strategy.

            Args:
                cls: The model class (automatically passed by Pydantic)
                value: The field value being validated
                info: Validation context info containing field_name and other metadata

            Returns:
                The processed value (whitespace handled according to strategy)

            Raises:
                ValueError: If the processed value is empty or whitespace-only
            """
            # Allow None values to pass through (for optional fields)
            if value is None:
                return value

            # Only process string values
            if not isinstance(value, str):
                return value

            # Get the current field name being validated
            field_name = info.field_name

            # Look up the strategy for this specific field
            strategy = field_configs.get(field_name)

            # Apply the appropriate whitespace processing
            if strategy == "strict":
                # Remove ALL whitespace: "hello world" -> "helloworld"
                value = "".join(value.split())

            elif strategy == "trimmed":
                # Only remove leading/trailing: "  hello world  " -> "hello world"
                value = value.strip()

            else:
                # This should never happen if using proper type hints
                raise ValueError(f"Invalid strategy '{strategy}' for field '{field_name}'")

            # After processing, reject empty strings
            if value == "":
                raise ValueError(f"{field_name} cannot be empty or whitespace only")

            return value

    return StringValidatorsMixin
