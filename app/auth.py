from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException
from typing import Annotated
from .models import User
from sqlmodel import select, Session
import secrets
from .database import get_session

# SessionDep is a repeated line, dependencies.py already has the exact same alias but importing it doesn't work due to a a circular import issue, 
# all other solutions to fix the circular import had worse trade-offs

SessionDep = Annotated[Session, Depends(get_session)]

active_tokens = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

def fake_hash_password(password: str):
    return "fake_hash " + password

def verify_password(plain_password: str, hash_password: str) -> bool:
    return fake_hash_password(plain_password) == hash_password

def authenticate_user(username: str, password: str, session: SessionDep) -> User | None:
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        return None
    
    if not verify_password(password, user.password_hash):
        return None
    
    return user

def create_token(user_id: int) -> str:
    token = secrets.token_urlsafe(32)
    active_tokens[token] = user_id
    return token

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