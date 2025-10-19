from typing import Annotated, TypeVar, Type
from fastapi import HTTPException, Depends
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

def expense_dependency(expense_id: int, session: SessionDep):
    return get_object_or_404(model=Expense, object_id=expense_id, session=session)

def user_read_dependency(user_id: int, session: SessionDep):
    user = get_object_or_404(model=User, object_id=user_id, session=session)
    return UserRead.model_validate(user)

def user_dependency(user_id: int, session: SessionDep):
    return get_object_or_404(model=User, object_id=user_id, session=session)

ExpenseDep = Annotated[Expense, Depends(expense_dependency)]
UserReadDep = Annotated[UserRead, Depends(user_read_dependency)]
UserDep = Annotated[User, Depends(user_dependency)]