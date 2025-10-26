from fastapi.testclient import TestClient
from app.auth import authenticate_user, verify_password, create_token 
from fastapi import HTTPException
from pytest import raises
from app.models import User
from app.config import settings
import jwt

# ========================================
# Testing for authenticate_user from app/auth.py 
# ========================================
def test_authenticate_happy_path(test_db, test_user):
    result = authenticate_user("testuser", "testpassword", test_db)
    assert result.username == "testuser"

def test_authenticate_user_wrong_password(test_db, test_user):
    with raises(HTTPException) as exc_info:
        authenticate_user("testuser", "wrongpassword", test_db)

    assert exc_info.value.status_code == 401
    
def test_authenticate_user_not_found(test_db, test_user):
    with raises(HTTPException) as exc_info:
        authenticate_user("nonexistantuser", "testpassword", test_db)
    
    assert exc_info.value.status_code == 401

# ========================================
# Testing for verify_password from app/auth.py
# ========================================

def test_verify_password_happy_path(test_user: User):
    result = verify_password("testpassword", test_user.password_hash)
    assert result is True

def test_verify_password_wrong_password(test_user: User):
    result = verify_password("wrongpassword", test_user.password_hash)  
    assert result is False

# ========================================
# Testing for create_token from app/auth.py
# ========================================

def test_create_token():
    from typing import Any

    user_id = 1
    token = create_token(user_id=user_id)

    payload: dict[str, Any] = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

    assert int(payload["sub"]) == user_id
    assert "exp" in payload

def test_create_token_with_expiration():
    from datetime import timedelta, timezone, datetime
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