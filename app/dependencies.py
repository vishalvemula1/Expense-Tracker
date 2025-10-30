from .auth import verify_user, verify_expense, verify_category
from typing import Annotated
from fastapi import Depends
from .models import User, Expense, Category
from .database import SessionDep


__all__ = ["SessionDep",  "VerifiedOwnerDep", "VerifiedExpenseDep", "VerifiedCategoryDep"]
# Re-exported from database for centralized dependency access
SessionDep = SessionDep


VerifiedOwnerDep = Annotated[User, Depends(verify_user)]

VerifiedExpenseDep = Annotated[Expense, Depends(verify_expense)]

VerifiedCategoryDep = Annotated[Category, Depends(verify_category)]