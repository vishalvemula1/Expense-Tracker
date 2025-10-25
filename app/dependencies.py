from .auth import verify_user, verify_expense
from typing import Annotated
from fastapi import Depends
from .models import User, Expense
from .database import SessionDep

# Re-exported from database for centralized dependency access
SessionDep = SessionDep


VerifiedOwnerDep = Annotated[User, Depends(verify_user)]

VerifiedExpenseDep = Annotated[Expense, Depends(verify_expense)]