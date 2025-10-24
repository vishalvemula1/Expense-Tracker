from ..dependencies import *
from ..models import *
from ..auth import *

from fastapi import APIRouter, Query
from typing import Annotated
from sqlmodel import select
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/users", tags=["users"])



@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                session: SessionDep) -> Token:
    
    user =  authenticate_user(form_data.username, form_data.password, session)

    if not user:
        raise HTTPException(status_code=401, detail="username or password wrong")
    
    token = create_token(user.user_id)  # type: ignore
    return Token(access_token=token, token_type="bearer")
    

@router.post("/signup", response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep):
    
    hashed_password = get_password_hash(user.password)
    user_data_dict = user.model_dump(exclude={"password"})
    new_user = User.model_validate(user_data_dict, update={"password_hash": hashed_password})

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.get("/{user_id}", response_model=UserRead)
async def read_user(verified_user: VerifiedOwnerDep):
    return verified_user


@router.get("/", response_model=list[UserRead])
async def read_users(session: SessionDep, 
                     offset: int = 0, 
                     limit: Annotated[int, Query(le=100)] = 100):
    
    users = session.exec(select(User).limit(limit).offset(offset)).all()
    return list(users)


@router.put("/{user_id}", response_model=UserRead)
async def update_user(verified_user: VerifiedOwnerDep, 
                      update_request: UserUpdate, 
                      session: SessionDep):
    
    update_dict = update_request.model_dump(exclude_unset=True, exclude={"password"})
    if update_request.password:
        hashed_password = get_password_hash(update_request.password)
        update_dict['password_hash'] = hashed_password

    verified_user.sqlmodel_update(update_dict)

    session.add(verified_user)
    session.commit()
    session.refresh(verified_user)
    print("hello")
    return verified_user


@router.delete("/{user_id}")
async def delete_user(verified_user: VerifiedOwnerDep, session: SessionDep):
    session.delete(verified_user)
    session.commit()

    return "Deletion Successful"