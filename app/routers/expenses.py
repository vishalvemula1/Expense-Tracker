from ..dependencies import *
from fastapi import Query, APIRouter
from sqlmodel import select
from typing import Annotated
from ..models import *

router = APIRouter(prefix="/users/{user_id}/expenses", tags=["expenses"])

@router.get("/{expense_id}")
async def read_an_expense(expense: ExpenseDep):
    return expense

@router.post("/")
async def add_expense(user_id: int, expense: ExpenseCreate, user: UserDep, session: SessionDep):
    expense_data = Expense.model_validate(expense, update={"user_id": user_id})

    session.add(expense_data)
    session.commit()
    session.refresh(expense_data)

    return expense_data

@router.get("/")
async def read_expenses(user_id: int,
                        user: UserDep,
                        session: SessionDep, 
                        limit: Annotated[int, Query(le=100)] = 5,
                        offset: int = 0) -> list[Expense]:
    
    expenses = session.exec(
        select(Expense)
        .where(Expense.user_id == user_id)
        .limit(limit)
        .offset(offset)
        ).all()
    return list(expenses)

@router.delete("/{expense_id}")
async def delete_expense(expense: ExpenseDep, session: SessionDep):
    session.delete(expense)
    session.commit()

    return expense

@router.put("/{expense_id}")
async def update_expense(expense: ExpenseDep, update_request: ExpenseUpdate, session: SessionDep):
    update_data = update_request.model_dump(exclude_unset=True)

    expense.sqlmodel_update(update_data)
    expense.date_of_update = date.today()

    session.add(expense)
    session.commit()
    session.refresh(expense)

    return expense