from datetime import datetime, timedelta, timezone
from typing import Annotated, Any
from sqlmodel import select
from fastapi import Depends

import jwt
from jwt.exceptions import InvalidTokenError

from .exceptions import AppExceptions
from .database import SessionDep
from .models import User
from .security import verify_password, ACCESS_TOKEN_EXPIRE_MINUTES, SECRET_KEY, ALGORITHM, oauth2_scheme

def authenticate_user(username: str, password: str, session: SessionDep) -> User:
     
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()

    if not user:
        raise AppExceptions.InvalidUsernamePassword
    
    if not verify_password(password, user.password_hash):
        raise AppExceptions.InvalidUsernamePassword
    
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
    from .services.user_service import UserService

    try:
        payload: dict[str, Any] = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise AppExceptions.CredentialsException

    except InvalidTokenError:
        raise AppExceptions.CredentialsException

    user = UserService.get_user(user_id, session=session)
    return user
        

