from .auth import get_authenticated_user
from typing import Annotated
from fastapi import Depends, HTTPException
from .models import User, Expense, Category
from .database import SessionDep
from .services import get_expense, get_category

__all__ = ["SessionDep",  "VerifiedOwnerDep", "VerifiedExpenseDep", "VerifiedCategoryDep"]
# Re-exported from database for centralized dependency access
SessionDep = SessionDep

# User

def verify_user(user_id: int, authenticated_user: Annotated[User, Depends(get_authenticated_user)]) -> User: 
    if authenticated_user.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this request")
    return authenticated_user

VerifiedOwnerDep = Annotated[User, Depends(verify_user)]


# Expenses

def verify_expense(expense_id: int, user: Annotated[User, Depends(verify_user)], session: SessionDep) -> Expense: 
    return get_expense(expense_id=expense_id, user=user, session=session) 

VerifiedExpenseDep = Annotated[Expense, Depends(verify_expense)]

# Categories

def verify_category(category_id: int, user: Annotated[User, Depends(verify_user)], session: SessionDep) -> Category:
    return get_category(category_id=category_id, user=user, session=session)

VerifiedCategoryDep = Annotated[Category, Depends(verify_category)]

