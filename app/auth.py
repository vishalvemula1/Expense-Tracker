from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

import jwt 
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from .database import SessionDep
from .services import get_user
from .models import User, Expense, Category
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

pass_hash = PasswordHash.recommended()

credentials_exception = HTTPException(status_code=401, 
                                      detail="Could not validate credentials",
                                      headers={"WWW-Authenticate": "Bearer"})

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pass_hash.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pass_hash.hash(password)

def authenticate_user(username: str, password: str, session: SessionDep) -> User:
     
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    return user

def create_token(user_id: int,
                expires_delta: timedelta | None = None) -> str:
    
    to_encode: dict[str, str | int] = {"sub":  str(user_id)}
    
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta

    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode["exp"] = int(expire.timestamp()) 

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    

async def get_authenticated_user(token: Annotated[str, Depends(oauth2_scheme)], 
                                 session: SessionDep) -> User:
    
    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(user_id, session=session)
    return user
        

