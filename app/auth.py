from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated
from .dependencies import SessionDep
from .models import User
from sqlmodel import select
import secrets


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

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: SessionDep):
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
    

CurrentUserDep = Annotated[User, Depends(get_current_user)]