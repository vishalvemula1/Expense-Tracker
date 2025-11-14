from typing import TypeVar, Type
from fastapi import HTTPException
from sqlmodel import SQLModel, Session, select
from .models import Expense, User, UserCreate
from .models import Category
from .exceptions import AppExceptions, db_transaction
from .config import default_categories as defaults
from datetime import date
from .security import get_password_hash


def create_user_with_defaults(user: UserCreate, session: Session) -> User:
    with db_transaction(session, context="User Signup") as db:
        hashed_password = get_password_hash(user.password)
        user_data_dict = user.model_dump(exclude={"password"})
        new_user = User.model_validate(user_data_dict, update={"password_hash": hashed_password})

        session.add(new_user)
        session.flush()

        # Creating a default category for every new user called "Uncategorized"
        default_category = Category(name = defaults.DEFAULT_CATEGORY_NAME,
                                    user_id = new_user.user_id, # type: ignore
                                    description = defaults.DEFAULT_CATEGORY_DESCRIPTION,
                                    tag = defaults.DEFAULT_CATEGORY_TAG, # type: ignore
                                    date_of_entry = date.today(),
                                    is_default = True)
        
        session.add(default_category)
        session.commit()

    session.refresh(new_user)

    return new_user



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
        raise AppExceptions.Unauthorized
    return data
    
def get_category_or_default(category_id: int | None, user: User, session: Session) -> Category:
    if category_id is None:
        category = session.exec(select(Category).where(Category.user_id == user.user_id, Category.is_default == True)).first()
        if category is None:
            raise HTTPException(status_code=404, detail="Default category not found")
        return category
    
    data = get_object_or_404(model=Category, object_id=category_id, session=session)
    if data.user_id != user.user_id:
        raise AppExceptions.Unauthorized
    return data