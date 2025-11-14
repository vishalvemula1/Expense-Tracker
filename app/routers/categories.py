from fastapi import Query, APIRouter
from ..models import Category, CategoryCreate, CategoryUpdate, Expense, CategoryRead, ExpenseRead
from ..dependencies import VerifiedReadCategoryDep, SessionDep, VerifiedOwnerDep, VerifiedWriteCategoryDep
from ..exceptions import db_transaction

from sqlmodel import select
from typing import Annotated

category_router = APIRouter(prefix="/me/categories", tags=["categories"])

@category_router.post("/", response_model=CategoryRead)
async def create_category(new_category: CategoryCreate, 
                          verified_user: VerifiedOwnerDep, 
                          session: SessionDep) -> Category: 
    
    with db_transaction(session, context="Category Creation") as db:
        category_data = Category.model_validate(new_category, update={"user_id": verified_user.user_id})

        session.add(category_data)
        session.commit()

    session.refresh(category_data)

    return category_data


@category_router.get("/{category_id}", response_model=CategoryRead)
async def read_category(category: VerifiedReadCategoryDep) -> Category:
    return category


@category_router.put("/{category_id}", response_model=CategoryRead)
async def update_category(category: VerifiedWriteCategoryDep,
                          update_request: CategoryUpdate,
                          session: SessionDep) -> Category: 
    
    with db_transaction(session, context="Category Updation") as db:
        update_data = update_request.model_dump(exclude_unset=True)

        category.sqlmodel_update(update_data)
        
        session.add(category)
        session.commit()

    session.refresh(category)

    return category


@category_router.delete("/{category_id}")
async def delete_category(category: VerifiedWriteCategoryDep, 
                          session: SessionDep):
    
    session.delete(category)
    session.commit()

    return


@category_router.get("/", response_model=list[CategoryRead])
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

@category_router.get("/{category_id}/expenses", response_model=list[ExpenseRead])
async def read_all_expenses_from_category(category: VerifiedReadCategoryDep,
                                          session: SessionDep) -> list[Expense]:
    category_id = category.category_id
    statement = (select(Expense).where(Expense.category_id == category_id))
    
    data = session.exec(statement).all()

    return list(data)