from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from fastapi import Depends, FastAPI, HTTPException, status
from typing import Annotated
from dependencies import SessionDep, UserDep


def fake_hash_password(password: str):
    return "fake_hash " + password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

