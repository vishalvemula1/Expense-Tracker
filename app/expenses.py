from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated, Optional
from pydantic import BaseModel, Field
from datetime import date


PositiveAmount = Annotated[float, Field(ge= 0, description="Amount must be greater than zero")]
DateCheck = Annotated[date, Field(default_factory=date.today)]

class ExpenseBase(BaseModel):
    name: str
    amount: PositiveAmount
    category: str | None = None
    description: str | None = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    name: str | None = None
    amount: Optional[PositiveAmount] = None
    category: str | None = None
    description: str | None = None


class Expense(ExpenseBase):
    id: int
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None



app = FastAPI()


expenses = {}
def retrieve_expense(id: int):
    expense = expenses.get(id)
    if not expense:
        raise HTTPException(status_code=404, detail="ID not found in dict (retrieve)")
    return expense

next_id = 1

@app.post("/expenses")
async def add_expense(entry: ExpenseCreate):
    global next_id


    expense = Expense(id=next_id, **entry.model_dump())

    expenses[next_id] = expense

    next_id += 1
    return expense

@app.get("/expenses")
async def read_expenses(category: str | None = None,
                        min_amount: int | None = None,
                        max_amount: int | None = None):
    filtering = list(expenses.values())
    
    if category:
        filtering = [e for e in filtering if e.category == category]
    
    if min_amount:
        filtering = [e for e in filtering if e.amount >= min_amount]

    if max_amount:
        filtering = [e for e in filtering if e.amount <= max_amount]

    return filtering


@app.get("/expenses/{id}")
async def read_expense(expense: Annotated[Expense, Depends(retrieve_expense)]):
    return expense


@app.delete("/expenses/{id}")
async def delete_expense(expense: Annotated[Expense, Depends(retrieve_expense)]):
    deleted_expense = expenses.pop(expense.id)
    return deleted_expense


@app.put("/expenses/{id}")
async def update_expense(id: int, expense: Annotated[Expense, Depends(retrieve_expense)],
                         update_request: ExpenseUpdate):
    update = update_request.model_dump(exclude_unset=True)

    updated_expense = expense.model_copy(update=update)
    updated_expense.date_of_update = date.today()
    expenses[id] = updated_expense

    return updated_expense
