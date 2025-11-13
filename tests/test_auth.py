from app.auth import authenticate_user, create_token, get_authenticated_user
from app.security import verify_password
from fastapi import HTTPException
from pytest import raises
from app.models import User
import jwt
from sqlmodel import Session
import pytest

# ====================================================================
# Testing for authenticate_user from app/auth.py 
# ====================================================================
def test_authenticate_happy_path(test_db, test_user):
    result = authenticate_user("testuser", "testpassword", test_db)
    assert result.username == "testuser"

def test_authenticate_user_wrong_password(test_db, test_user):
    with raises(HTTPException) as exc_info:
        authenticate_user("testuser", "wrongpassword", test_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"

def test_authenticate_user_not_found(test_db, test_user):
    with raises(HTTPException) as exc_info:
        authenticate_user("nonexistantuser", "testpassword", test_db)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid username or password"


# ====================================================================
# Testing for verify_password from app/auth.py
# ====================================================================

def test_verify_password_happy_path(test_user: User):
    result = verify_password("testpassword", test_user.password_hash)
    assert result is True

def test_verify_password_wrong_password(test_user: User):
    result = verify_password("wrongpassword", test_user.password_hash)  
    assert result is False

# ====================================================================
# Testing for create_token from app/auth.py
# ====================================================================

def test_create_token():
    from app.config import settings
    from typing import Any

    user_id = 1
    token = create_token(user_id=user_id)

    payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert int(payload["sub"]) == user_id
    assert "exp" in payload

def test_create_token_with_expiration():
    from datetime import timedelta, timezone, datetime
    from app.config import settings
    from typing import Any

    user_id = 1
    time = 5
    expires_delta = timedelta(minutes=time)

    before = int(datetime.now(timezone.utc).timestamp())
    token = create_token(user_id=user_id, expires_delta=expires_delta)
    after = int(datetime.now(timezone.utc).timestamp())

    payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    expected_min = before + (time * 60)
    expected_max = after + (time * 60)

    assert expected_min <= payload["exp"] <= expected_max

# ====================================================================
# Testing for get_authenticated_user from app/auth.py
# ====================================================================

@pytest.mark.asyncio
async def test_get_authenticated_user_happy_path(test_db: Session, test_user: User):
    user_id = test_user.user_id
    assert user_id is not None

    token = create_token(user_id)

    result = await get_authenticated_user(token, test_db)
    assert result == test_user

@pytest.mark.asyncio
async def test_get_authenticated_user_wrong_user(test_db: Session, test_user: User):

    token = "stringforme"

    with raises(HTTPException) as exc_info:
        await get_authenticated_user(token, test_db)

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"

@pytest.mark.asyncio
async def test_get_authenticated_user_expired_token(test_db: Session, test_user: User):
    from datetime import timedelta

    user_id = test_user.user_id
    assert user_id is not None

    token = create_token(user_id, expires_delta=timedelta(seconds=-1))

    with raises(HTTPException) as exc_info:
        await get_authenticated_user(token, test_db)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Could not validate credentials"
    
@pytest.mark.asyncio
async def test_get_authenticated_user_no_user(test_db: Session, test_user: User):
    user_id = 3

    token = create_token(user_id)

    with raises(HTTPException) as exc_info:
        await get_authenticated_user(token, test_db)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "User was not found"