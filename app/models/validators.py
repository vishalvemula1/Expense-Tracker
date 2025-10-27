from pydantic import field_validator


# ==========================================
# Validator Function & Mixins
# ==========================================
def validate_no_empty_strings(v):
    """Strip whitespace and reject empty strings"""
    if v is None:
        return v
    
    if isinstance(v, str):
        v = v.strip()
    
    if isinstance(v, str) and v == "":
        raise ValueError("Cannot be empty or whitespace only")
    
    return v


def create_non_empty_validator_mixin(*fields):
    """Factory function to create a mixin for specific fields"""
    class NoEmptyStringsMixin:
        """Adds field validators to make sure that the given fields
        are not empty strings"""
        
        @field_validator(*fields, mode="before")
        @classmethod
        def validate_user_fields(cls, v):
            return validate_no_empty_strings(v)

    return NoEmptyStringsMixin

