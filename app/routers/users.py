from ..dependencies import *
from fastapi import APIRouter, Query
from typing import Annotated
from sqlmodel import select
from ..models import *
from ..auth import fake_hash_password


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/",response_model=UserRead)
async def create_user(user: UserCreate, session: SessionDep):
    hashed_password = fake_hash_password(user.password)
    user_data_dict = user.model_dump(exclude={"password"})
    new_user = User.model_validate(user_data_dict, update={"password_hash": hashed_password})

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user

@router.get("/{user_id}", response_model=UserRead)
async def read_user(user: UserDep):
    return user


@router.get("/", response_model=list[UserRead])
async def read_users(session: SessionDep, 
                     offset: int = 0, 
                     limit: Annotated[int, Query(le=100)] = 100):
    
    users = session.exec(select(User).limit(limit).offset(offset)).all()
    return list(users)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user: UserDep, update_request: UserUpdate, session: SessionDep):
    update_dict = update_request.model_dump(exclude_unset=True, exclude={"password"})
    if update_request.password:
        hashed_password = fake_hash_password(update_request.password)
        update_dict['password_hash'] = hashed_password

    user.sqlmodel_update(update_dict)

    session.add(user)
    session.commit()
    session.refresh(user)
    print("hello")
    return user

@router.delete("/{user_id}")
async def delete_user(user: UserDep, session: SessionDep):
    session.delete(user)
    session.commit()

    return "Deletion Successful"