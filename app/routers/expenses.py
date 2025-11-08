from ..dependencies import SessionDep, VerifiedExpenseDep, VerifiedOwnerDep
from fastapi import Query, APIRouter
from sqlmodel import select
from typing import Annotated
from ..models import Expense, ExpenseCreate, ExpenseUpdate
from datetime import date
from ..services import get_category_or_default

router = APIRouter(prefix="/users/{user_id}/expenses", tags=["expenses"])

@router.get("/{expense_id}")
async def read_an_expense(expense: VerifiedExpenseDep) -> Expense:
    return expense

@router.post("/")
async def add_expense(verified_user: VerifiedOwnerDep, 
                      new_expense: ExpenseCreate, 
                      session: SessionDep) -> Expense:
    
    category_id = new_expense.category_id
    category = get_category_or_default(category_id=category_id, user=verified_user, session=session)


    expense_data = Expense.model_validate(new_expense, update={"user_id": verified_user.user_id, "category_id": category.category_id})

    session.add(expense_data)
    session.commit()
    session.refresh(expense_data)

    return expense_data

@router.get("/")
async def read_all_expenses(verified_user: VerifiedOwnerDep,
                        session: SessionDep, 
                        limit: Annotated[int, Query(le=100)] = 5,
                        offset: int = 0) -> list[Expense]:
    
    expenses = session.exec(
        select(Expense)
        .where(Expense.user_id == verified_user.user_id)
        .limit(limit)
        .offset(offset)
        ).all()
    return list(expenses)

@router.delete("/{expense_id}")
async def delete_expense(expense: VerifiedExpenseDep,  
                         session: SessionDep) -> Expense:
    
    session.delete(expense)
    session.commit()

    return expense

@router.put("/{expense_id}")
async def update_expense(expense: VerifiedExpenseDep,
                         user: VerifiedOwnerDep, 
                         update_request: ExpenseUpdate,  
                         session: SessionDep) -> Expense:
    
    category_id = update_request.category_id
    category = get_category_or_default(category_id=category_id, user=user, session=session)

    update_data = update_request.model_dump(exclude_unset=True)
    update_data.update({"category_id": category.category_id})

    expense.sqlmodel_update(update_data)
    expense.date_of_update = date.today()

    session.add(expense)
    session.commit()
    session.refresh(expense)

    return expense