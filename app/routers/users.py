from ..dependencies import *
from fastapi import APIRouter, Query
from typing import Annotated
from sqlmodel import select
from ..models import *

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/")
async def create_user(user: UserCreate, session: SessionDep):
    user_data = User.model_validate(user)

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