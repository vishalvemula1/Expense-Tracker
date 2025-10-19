from typing import Annotated, Optional
from datetime import date
from sqlmodel import Field, SQLModel

PositiveAmount = Annotated[float, Field(ge= 0, description="Amount must be greater than zero", default=0)]
DateCheck = Annotated[date, Field(default_factory=date.today)]

class ExpenseBase(SQLModel):
    name: str 
    amount: PositiveAmount
    category: str | None = None
    description: str | None = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    name: str | None = None
    amount: Optional[PositiveAmount] = None
    category: str | None = None
    description: str | None = None


class Expense(ExpenseBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None
