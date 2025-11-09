from fastapi import Query, APIRouter
from ..models import Category, CategoryCreate, CategoryUpdate, Expense
from ..dependencies import VerifiedCategoryDep, SessionDep, VerifiedOwnerDep
from ..exceptions import AppExceptions, db_transaction

from sqlmodel import select
from typing import Annotated

router = APIRouter(prefix="/me/categories", tags=["categories"])

@router.post("/")
async def create_category(new_category: CategoryCreate, 
                          verified_user: VerifiedOwnerDep, 
                          session: SessionDep) -> Category: 
    
    with db_transaction(session, context="Category Creation") as db:
        category_data = Category.model_validate(new_category, update={"user_id": verified_user.user_id})

        session.add(category_data)
        session.commit()

    session.refresh(category_data)

    return category_data


@router.get("/{category_id}")
async def read_category(category: VerifiedCategoryDep) -> Category:
    return category


@router.put("/{category_id}")
async def update_category(category: VerifiedCategoryDep,
                          update_request: CategoryUpdate,
                          session: SessionDep) -> Category: 
    
    if category.is_default:
        raise AppExceptions.DefaultCategoryUneditable
    
    with db_transaction(session, context="Category Updation") as db:
        update_data = update_request.model_dump(exclude_unset=True)

        category.sqlmodel_update(update_data)
        
        session.add(category)
        session.commit()

    session.refresh(category)

    return category


@router.delete("/{category_id}")
async def delete_category(category: VerifiedCategoryDep, 
                          session: SessionDep):
    
    if category.is_default:
        raise AppExceptions.DefaultCategoryUneditable
    
    session.delete(category)
    session.commit()

    return


@router.get("/")
async def read_all_categories(user: VerifiedOwnerDep, 
                              session: SessionDep,
                              limit: Annotated[int, Query(le=100)] = 5,
                              offset: int = 0) -> list[Category]:

    statement = (select(Category)
    .where(Category.user_id == user.user_id)
    .limit(limit)
    .offset(offset))

    data = session.exec(statement).all()

    return list(data)

@router.get("/{category_id}/expenses")
async def read_all_expenses_from_category(category: VerifiedCategoryDep,
                                          session: SessionDep) -> list[Expense]:
    category_id = category.category_id
    statement = (select(Expense).where(Expense.category_id == category_id))
    
    data = session.exec(statement).all()

    return list(data)