from .auth import verify_user, verify_expense
from typing import Annotated
from fastapi import Depends
from sqlmodel import Session
from .models import User, Expense
from .database import get_session

SessionDep = Annotated[Session, Depends(get_session)]

VerifiedOwnerDep = Annotated[User, Depends(verify_user)]

VerifiedExpenseDep = Annotated[Expense, Depends(verify_expense)]