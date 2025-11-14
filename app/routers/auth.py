from ..dependencies import SessionDep
from ..models import UserRead, UserCreate, User, Token
from ..auth import (authenticate_user, create_token)
from ..services import create_user_with_defaults

from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                session: SessionDep) -> Token:
    
    user = authenticate_user(form_data.username, form_data.password, session)
    
    token = create_token(user.user_id) #type: ignore
    return Token(access_token=token, token_type="bearer")
    

@auth_router.post("/signup", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep) -> User:
    return create_user_with_defaults(user, session)