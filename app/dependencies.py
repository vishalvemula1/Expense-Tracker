from .auth import get_authenticated_user
from typing import Annotated
from fastapi import Depends
from .models import User
from .database import SessionDep

SessionDep = SessionDep

VerifiedOwnerDep = Annotated[User, Depends(get_authenticated_user)]