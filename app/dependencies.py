from typing import Annotated, TypeVar, Type
from fastapi import HTTPException, Depends
from sqlmodel import SQLModel, Session
from .database import get_session
from .models import Expense, User

SessionDep = Annotated[Session, Depends(get_session)]

ModelType = TypeVar('ModelType', bound=SQLModel)

def get_object_or_404(model: Type[ModelType], object_id: int, session: SessionDep) -> ModelType:
    object_data = session.get(model, object_id)
    if not object_data:
        raise HTTPException(status_code=404, detail=f"{model.__name__} was not found")
    return object_data

def get_user(user_id: int, session: SessionDep) -> User:
    return get_object_or_404(model=User, object_id=user_id, session=session)


def get_expense(user_id: int, user: Depends(get_user), expense_id: int, session: SessionDep) -> Expense: # type: ignore
    data = get_object_or_404(model=Expense, object_id=expense_id, session=session)
    if data.user_id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return data
    

