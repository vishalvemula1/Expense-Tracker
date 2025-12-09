from ..models import UserRead, UserCreate, User, Token
from ..services import AuthService, get_auth_service

from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm


auth_router = APIRouter(prefix="/auth", tags=["auth"])

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]

@auth_router.post("/login", response_model=Token)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                svc: AuthServiceDep) -> Token:
    
    return svc.login(form_data)
    

@auth_router.post("/signup", response_model=UserRead)
async def create_user(user: UserCreate, 
                      svc: AuthServiceDep) -> User:
    
    return svc.create_user_with_defaults(user)