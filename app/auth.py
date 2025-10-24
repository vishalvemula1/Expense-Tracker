from datetime import datetime, timedelta, timezone
from typing import Annotated
from sqlmodel import select
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException

import jwt 
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from .dependencies import SessionDep, get_user
from .models import User
from .config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

pass_hash = PasswordHash.recommended()


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

def create_token(user_id: int,
                expires_delta: timedelta | None = None):
    to_encode = {"sub":  str(user_id)}
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    to_encode["exp"] = expire #type: ignore

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
    

async def get_authenticated_user(token: Annotated[str, Depends(oauth2_scheme)], 
                                 session: SessionDep):
    credentials_exception = HTTPException(status_code=401, 
                                            detail="Could not validate credentials",
                                            headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except InvalidTokenError:
        raise credentials_exception
    
    user = get_user(user_id, session=session)
    return user
        

AuthenticatedUserDep = Annotated[User, Depends(get_authenticated_user)]

def verify_user(user_id: int, current_user: AuthenticatedUserDep):
    if current_user.user_id != user_id:
        raise HTTPException(status_code=401, detail="Not authorized for this request")
    return current_user

VerifiedOwnerDep = Annotated[User, Depends(verify_user)]  