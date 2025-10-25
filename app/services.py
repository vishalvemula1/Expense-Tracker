from typing import TypeVar, Type
from fastapi import HTTPException, Depends
from sqlmodel import SQLModel
from .database import SessionDep
from .models import Expense, User
from typing import Annotated

ModelType = TypeVar('ModelType', bound=SQLModel)

def get_object_or_404(model: Type[ModelType], object_id: int, session: SessionDep) -> ModelType:
    object_data = session.get(model, object_id)
    if not object_data:
        raise HTTPException(status_code=404, detail=f"{model.__name__} was not found")
    return object_data

def get_user(user_id: int, session: SessionDep) -> User:
    return get_object_or_404(model=User, object_id=user_id, session=session)


def get_expense(expense_id: int, user: Annotated[User, Depends(get_user)], session: SessionDep) -> Expense:
    data = get_object_or_404(model=Expense, object_id=expense_id, session=session)
    if data.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized to perform this action")
    return data
    

