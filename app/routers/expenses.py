from fastapi import Query, APIRouter, Depends
from typing import Annotated
from ..models import Expense, ExpenseCreate, ExpenseUpdate, ExpenseRead
from ..services import ExpenseService, get_expense_service

expense_router = APIRouter(prefix="/me/expenses", tags=["expenses"])

ExpenseServiceDep = Annotated[ExpenseService, Depends(get_expense_service)]

@expense_router.get("/{expense_id}")
async def get_expense(svc: ExpenseServiceDep,
                      expense_id: int) -> Expense:

    return svc.get(expense_id)

@expense_router.post("/", response_model=ExpenseRead)
async def create_expense(svc: ExpenseServiceDep,
                         new_expense: ExpenseCreate) -> Expense:

    return svc.create(new_expense)

@expense_router.get("/", response_model=list[ExpenseRead])
async def list_expenses(svc: ExpenseServiceDep,
                        limit: Annotated[int, Query(le=100)] = 5,
                        offset: int = 0) -> list[Expense]:

    return svc.list(limit, offset)

@expense_router.delete("/{expense_id}")
async def delete_expense(svc: ExpenseServiceDep, 
                         expense_id: int):
    svc.delete(expense_id)

@expense_router.put("/{expense_id}", response_model=ExpenseRead)
async def update_expense(svc: ExpenseServiceDep,
                         expense_id: int,
                         update_request: ExpenseUpdate) -> Expense:

    return svc.update(expense_id, update_request)