from typing import Annotated, TypeVar, Type
from fastapi import HTTPException, Depends, status
from sqlmodel import SQLModel, Session
from .database import get_session
from .models import Expense, User, UserRead

SessionDep = Annotated[Session, Depends(get_session)]

ModelType = TypeVar('ModelType', bound=SQLModel)

def get_object_or_404(model: Type[ModelType], object_id: int, session: SessionDep):
    object_data = session.get(model, object_id)
    if not object_data:
        raise HTTPException(status_code=404, detail=f"{model.__name__} was not found")
    return object_data

def user_dependency(user_id: int, session: SessionDep):
    return get_object_or_404(model=User, object_id=user_id, session=session)

UserDep = Annotated[User, Depends(user_dependency)]

def expense_dependency(user_id: int, user: UserDep, expense_id: int, session: SessionDep):
    data = get_object_or_404(model=Expense, object_id=expense_id, session=session)
    if data.user_id != user_id:
        raise HTTPException(status_code=403, detail="Unauthorized access")
    return data
    

ExpenseDep = Annotated[Expense, Depends(expense_dependency)]