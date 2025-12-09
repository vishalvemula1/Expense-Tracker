from ..models import UserRead, User, UserUpdate
from ..services import UserService, get_user_service
from typing import Annotated
from fastapi import APIRouter, Depends



user_router = APIRouter(tags=["users"])

UserServiceDep = Annotated[UserService, Depends(get_user_service)]

@user_router.get("/me", response_model=UserRead)
async def get_user(svc: UserServiceDep) -> User:
    return svc.get()

@user_router.put("/me", response_model=UserRead)
async def update_user(update_request: UserUpdate,
                      svc: UserServiceDep) -> User:

    return svc.update(update_request)

@user_router.delete("/me")
async def delete_user(svc: UserServiceDep):
    svc.delete()