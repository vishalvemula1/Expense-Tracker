from ..dependencies import *
from fastapi import APIRouter, Query
from typing import Annotated
from sqlmodel import select
from ..models import *
from ..auth import get_password_hash, #create_token
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import *

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/login")
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
                session: SessionDep):
    user =  authenticate_user(form_data.username, form_data.password, session)
    if not user:
        raise HTTPException(status_code=401, detail="username or password wrong")
    
    token = create_token(user.user_id)  # type: ignore

    return {"access_token": token, "token_type": "bearer"}
    


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
async def read_user(user: UserDep, verification: VerifiedOwnerDep):
    return user


@router.get("/", response_model=list[UserRead])
async def read_users(session: SessionDep, 
                     offset: int = 0, 
                     limit: Annotated[int, Query(le=100)] = 100):
    
    users = session.exec(select(User).limit(limit).offset(offset)).all()
    return list(users)

@router.put("/{user_id}", response_model=UserRead)
async def update_user(user: UserDep, 
                      update_request: UserUpdate, 
                      session: SessionDep, 
                      verification: VerifiedOwnerDep):
    update_dict = update_request.model_dump(exclude_unset=True, exclude={"password"})
    if update_request.password:
        hashed_password = get_password_hash(update_request.password)
        update_dict['password_hash'] = hashed_password

    user.sqlmodel_update(update_dict)

    session.add(user)
    session.commit()
    session.refresh(user)
    print("hello")
    return user

@router.delete("/{user_id}")
async def delete_user(user: UserDep, session: SessionDep, verification: VerifiedOwnerDep):
    session.delete(user)
    session.commit()

    return "Deletion Successful"