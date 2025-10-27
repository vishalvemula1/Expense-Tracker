from typing import TypeVar, Type
from fastapi import HTTPException
from sqlmodel import SQLModel, Session
from .models import Expense, User

ModelType = TypeVar('ModelType', bound=SQLModel)

def get_object_or_404(model: Type[ModelType], object_id: int, session: Session) -> ModelType:
    object_data = session.get(model, object_id)
    if not object_data:
        raise HTTPException(status_code=404, detail=f"{model.__name__} was not found")
    return object_data

def get_user(user_id: int, session: Session) -> User:
    return get_object_or_404(model=User, object_id=user_id, session=session)


def get_expense(expense_id: int, user: User, session: Session) -> Expense:
    data = get_object_or_404(model=Expense, object_id=expense_id, session=session)
    if data.user_id != user.user_id:
        raise HTTPException(status_code=403, detail="Not authorized for this request")
    return data
    