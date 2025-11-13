from .auth import get_authenticated_user
from typing import Annotated
from fastapi import Depends
from .models import User, Expense, Category
from .database import SessionDep
from .services import get_expense, get_category_or_default
from .exceptions import AppExceptions

# Re-exported from database for centralized dependency access
SessionDep = SessionDep

# User 
VerifiedOwnerDep = Annotated[User, Depends(get_authenticated_user)]


# Expenses

def verify_expense(expense_id: int, user: VerifiedOwnerDep, session: SessionDep) -> Expense: 
    return get_expense(expense_id=expense_id, user=user, session=session) 

VerifiedExpenseDep = Annotated[Expense, Depends(verify_expense)]

# Categories

def verify_category(category_id: int, user: VerifiedOwnerDep, session: SessionDep) -> Category:
    return get_category_or_default(category_id=category_id, user=user, session=session)

VerifiedReadCategoryDep = Annotated[Category, Depends(verify_category)]
"""Verifies if the category exists and belongs to the user and doesn't check for if the category is default as this dependency is only meant to be used for read purposes, use VerifiedWriteCategoryDep
for write endpoints or use cases as it prevents default category from being tampered with"""

def verify_write_category(category: VerifiedReadCategoryDep) -> Category:
    if category.is_default:
        raise AppExceptions.DefaultCategoryUneditable
    return category

VerifiedWriteCategoryDep = Annotated[Category, Depends(verify_write_category)] 
"""Verifies category and then checks if the category is default and throws and exception if it is; to avoid default category from being edited or tampered with"""