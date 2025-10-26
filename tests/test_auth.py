from fastapi.testclient import TestClient
from app.auth import authenticate_user, verify_password, get_password_hash
from fastapi import HTTPException
from pytest import raises
from app.models import User

# ========================================
# Testing for authenticate_user function from app/auth.py 
# ========================================
def test_authenticate_user(test_db, test_user):
    result = authenticate_user("testuser", "testpassword", test_db)
    assert result.username == "testuser"

def test_authenticate_user_wrong_password(test_db, test_user):
    with raises(HTTPException) as exc_info:
        authenticate_user("testuser", "wrongpassword", test_db)

    assert exc_info.value.status_code == 401
    
def test_authenticate_user_not_found(test_db):
    with raises(HTTPException) as exc_info:
        authenticate_user("nonexistant", "testpassword", test_db)
    
    assert exc_info.value.status_code == 401

# ========================================
# Testing for verify_password from app/auth.py
# ========================================

def test_verify_password_right_password(test_user: User):
    result = verify_password("testpassword", test_user.password_hash)
    assert result is True

def test_verify_password_wrong_password(test_user: User):
    result = verify_password("wrongpassword", test_user.password_hash)  
    assert result is False

