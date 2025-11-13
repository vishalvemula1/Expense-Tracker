from ..dependencies import SessionDep, VerifiedOwnerDep
from ..models import UserRead, UserCreate, User, UserUpdate, Token
from ..auth import (authenticate_user, get_password_hash, create_token)
from ..models import Category
from ..config import default_categories as defaults
from ..exceptions import db_transaction

from fastapi import APIRouter, Query, Depends
from typing import Annotated
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm
from datetime import date


auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                session: SessionDep) -> Token:
    
    user = authenticate_user(form_data.username, form_data.password, session)
    
    token = create_token(user.user_id) #type: ignore
    return Token(access_token=token, token_type="bearer")
    

@auth_router.post("/signup", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep) -> User:

    with db_transaction(session, context="User Signup") as db:
        hashed_password = get_password_hash(user.password)
        user_data_dict = user.model_dump(exclude={"password"})
        new_user = User.model_validate(user_data_dict, update={"password_hash": hashed_password})

        session.add(new_user)
        session.flush()

        # Creating a default category for every new user called "Uncategorized"
        default_category = Category(name = defaults.DEFAULT_CATEGORY_NAME,
                                    user_id = new_user.user_id, # type: ignore
                                    description = defaults.DEFAULT_CATEGORY_DESCRIPTION,
                                    tag = defaults.DEFAULT_CATEGORY_TAG, # type: ignore
                                    date_of_entry = date.today(),
                                    is_default = True)
        
        session.add(default_category)
        session.commit()

    session.refresh(new_user)

    return new_user


router = APIRouter(tags=["users"])

@router.get("/me", response_model=UserRead)
async def read_user(verified_user: VerifiedOwnerDep) -> User:
    return verified_user


@router.get("/", response_model=list[UserRead])
async def read_users(session: SessionDep, 
                     offset: int = 0, 
                     limit: Annotated[int, Query(le=100)] = 100) -> list[User]:
    
    users = session.exec(select(User).limit(limit).offset(offset)).all()
    return list(users)


@router.put("/me", response_model=UserRead)
async def update_user(verified_user: VerifiedOwnerDep, 
                      update_request: UserUpdate, 
                      session: SessionDep) -> User:
    
    with db_transaction(session, context="User Updation") as db:
        update_dict = update_request.model_dump(exclude_unset=True, exclude={"password"})
        
        if update_request.password:
            hashed_password = get_password_hash(update_request.password)
            update_dict['password_hash'] = hashed_password

        verified_user.sqlmodel_update(update_dict)

        session.add(verified_user)
        session.commit()

    session.refresh(verified_user)
    return verified_user


@router.delete("/me")
async def delete_user(verified_user: VerifiedOwnerDep, session: SessionDep):
    session.delete(verified_user)
    session.commit()

    return