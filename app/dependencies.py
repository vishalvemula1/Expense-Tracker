from .auth import get_authenticated_user
from typing import Annotated
from fastapi import Depends
from .models import User
from .database import SessionDep

# re-export for centralizing dependency declarations, `SessionDep = SessionDep` doesn't serve any functional purpose, it's just for anyone to be able to see all important
# dependencies in one place
SessionDep = SessionDep

VerifiedOwnerDep = Annotated[User, Depends(get_authenticated_user)]