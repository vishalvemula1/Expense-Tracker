from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlmodel import select, Session
import secrets
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

import jwt 
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from .dependencies import SessionDep
from .database import get_session
from .models import User


SECRET_KEY = "0ccad8070c738ed9a9263785947e738201986ec17435411501ad7725992813b9"
ALGORITHM = "HS256"
ACESS_TOKEN_EXPIRE_MINUTES = 30

active_tokens = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

pass_hash = PasswordHash.recommended()

# def password_hasher(password: str):
#     return hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pass_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str):
    return pass_hash.hash(password)

def authenticate_user(username: str, password: str, session: SessionDep) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

# def create_token(user_id: int) -> str:
#     token = secrets.token_urlsafe(32)
#     active_tokens[token] = user_id
#     return token



async def get_authenticated_user(token: Annotated[str, Depends(oauth2_scheme)], 
                                 session: SessionDep):
    if token not in active_tokens:
        raise HTTPException(
            status_code=401,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = active_tokens[token]
    user = session.get(User, user_id)

    if not user:
        active_tokens.pop(token)
        raise HTTPException(
            status_code=401, 
            detail="user not found"
        )
    
    return user


AuthenticatedUserDep = Annotated[User, Depends(get_authenticated_user)]

def verify_user(user_id: int, current_user: AuthenticatedUserDep):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=401, detail="Not authorized for this request")
    return current_user

VerifiedOwnerDep = Annotated[User, Depends(verify_user)]  