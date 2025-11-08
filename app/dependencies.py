from .auth import get_authenticated_user
from typing import Annotated
from fastapi import Depends
from .models import User, Expense, Category
from .database import SessionDep
from .services import get_expense, get_category_or_default
from .exceptions import AppExceptions

# Re-exported from database for centralized dependency access
SessionDep = SessionDep

# User - simplified to just authenticate without user_id path parameter
VerifiedOwnerDep = Annotated[User, Depends(get_authenticated_user)]


# Expenses

def verify_expense(expense_id: int, user: Annotated[User, Depends(get_authenticated_user)], session: SessionDep) -> Expense: 
    return get_expense(expense_id=expense_id, user=user, session=session) 

VerifiedExpenseDep = Annotated[Expense, Depends(verify_expense)]

# Categories

def verify_category(category_id: int, user: Annotated[User, Depends(get_authenticated_user)], session: SessionDep) -> Category:
    return get_category_or_default(category_id=category_id, user=user, session=session)

VerifiedCategoryDep = Annotated[Category, Depends(verify_category)]

