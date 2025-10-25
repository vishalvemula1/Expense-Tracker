from ..dependencies import *
from fastapi import Query, APIRouter
from sqlmodel import select
from typing import Annotated
from ..models import *
from ..auth import VerifiedOwnerDep

router = APIRouter(prefix="/users/{user_id}/expenses", tags=["expenses"])

@router.get("/{expense_id}")
async def read_an_expense(expense: ExpenseDep, verification: VerifiedOwnerDep) -> Expense:
    return expense

@router.post("/")
async def add_expense(verified_user: VerifiedOwnerDep, 
                      expense: ExpenseCreate, 
                      session: SessionDep) -> Expense:
    
    expense_data = Expense.model_validate(expense, update={"user_id": verified_user.user_id})

    session.add(expense_data)
    session.commit()
    session.refresh(expense_data)

    return expense_data

@router.get("/")
async def read_expenses(verified_user: VerifiedOwnerDep,
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
async def delete_expense(expense: ExpenseDep, 
                         verification: VerifiedOwnerDep, 
                         session: SessionDep) -> Expense:
    
    session.delete(expense)
    session.commit()

    return expense

@router.put("/{expense_id}")
async def update_expense(expense: ExpenseDep, 
                         update_request: ExpenseUpdate, 
                         verification: VerifiedOwnerDep, 
                         session: SessionDep) -> Expense:
    
    update_data = update_request.model_dump(exclude_unset=True)

    expense.sqlmodel_update(update_data)
    expense.date_of_update = date.today()

    session.add(expense)
    session.commit()
    session.refresh(expense)

    return expense