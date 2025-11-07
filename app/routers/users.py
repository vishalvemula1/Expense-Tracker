from ..dependencies import *
from ..models import UserRead, UserCreate, User, UserUpdate, Token
from ..auth import (authenticate_user, get_password_hash, create_token)
from ..models import Category
from ..config import default_categories as defaults

from fastapi import APIRouter, Query, Depends, HTTPException
from typing import Annotated
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from datetime import date


router = APIRouter(prefix="/users", tags=["users"])



@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                session: SessionDep) -> Token:
    
    user = authenticate_user(form_data.username, form_data.password, session)
    
    token = create_token(user.user_id) #type: ignore
    return Token(access_token=token, token_type="bearer")
    

@router.post("/signup", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep) -> User:
    try: 
        hashed_password = get_password_hash(user.password)
        user_data_dict = user.model_dump(exclude={"password"})
        new_user = User.model_validate(user_data_dict, update={"password_hash": hashed_password})

        session.add(new_user)
        session.commit()
        session.refresh(new_user)

        # Creating a default category for every new user called "Uncategorized"
        default_category = Category(name = defaults.DEFAULT_CATEGORY_NAME,
                                    user_id = new_user.user_id, # type: ignore
                                    description = defaults.DEFAULT_CATEGORY_DESCRIPTION,
                                    tag = defaults.DEFAULT_CATEGORY_TAG, # type: ignore
                                    date_of_entry = date.today(),
                                    is_default = True)
        
        session.add(default_category)
        session.commit()
        session.refresh(default_category)

        return new_user
    
    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists"
        )


@router.get("/{user_id}", response_model=UserRead)
async def read_user(verified_user: VerifiedOwnerDep) -> User:
    return verified_user


@router.get("/", response_model=list[UserRead])
async def read_users(session: SessionDep, 
                     offset: int = 0, 
                     limit: Annotated[int, Query(le=100)] = 100) -> list[User]:
    
    users = session.exec(select(User).limit(limit).offset(offset)).all()
    return list(users)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(verified_user: VerifiedOwnerDep, 
                      update_request: UserUpdate, 
                      session: SessionDep) -> User:
    try:
        update_dict = update_request.model_dump(exclude_unset=True, exclude={"password"})
        if update_request.password:
            hashed_password = get_password_hash(update_request.password)
            update_dict['password_hash'] = hashed_password

        verified_user.sqlmodel_update(update_dict)

        session.add(verified_user)
        session.commit()
        session.refresh(verified_user)
        return verified_user

    except IntegrityError:
        session.rollback()
        raise HTTPException(
            status_code=409,
            detail="Username or email already exists"
        )


@router.delete("/{user_id}")
async def delete_user(verified_user: VerifiedOwnerDep, session: SessionDep) -> str:
    session.delete(verified_user)
    session.commit()

    return "Deletion Successful"