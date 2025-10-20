from ..dependencies import *
from fastapi import APIRouter, Query
from typing import Annotated
from sqlmodel import select
from ..models import *
from ..auth import fake_hash_password


router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user(user: UserCreate, session: SessionDep):
    original_password = user.password
    create_data = user.model_dump(exclude={"password"})
    hashed_password = fake_hash_password(original_password)

    user_data = User.model_validate(create_data, update={"password_hash": hashed_password})

    session.add(user_data)
    session.commit()
    session.refresh(user_data)

    return user_data

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
    update_data = update_request.model_dump(exclude_unset=True)

    user.sqlmodel_update(update_data)

    session.add(user)
    session.commit()
    session.refresh(user)

    return user

@router.delete("/{user_id}")
async def delete_user(user: UserDep, session: SessionDep):
    session.delete(user)
    session.commit()

    return "Deletion Successful"