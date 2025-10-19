from ..dependencies import *
from fastapi import Query, APIRouter
from sqlmodel import select
from typing import Annotated
from ..models import *

router = APIRouter(prefix="/expenses", tags=["expenses"])

@router.get("/{expense_id}")
async def read_an_expense(expense: ExpenseDep):
    return expense

@router.post("/")
async def add_expense(expense: ExpenseCreate, session: SessionDep):
    expense_data = Expense.model_validate(expense)

    session.add(expense_data)
    session.commit()
    session.refresh(expense_data)

    return expense_data

@router.get("/")
async def read_expenses(session: SessionDep, 
                        limit: Annotated[int, Query(le=100)] = 5,
                        offset: int = 0) -> list[Expense]:
    
    expenses = session.exec(select(Expense).limit(limit).offset(offset)).all()
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