from typing import Annotated, Optional
from .validators import create_string_validators
from datetime import date
from sqlmodel import Field, SQLModel
from .user import PositiveAmount


DateCheck = Annotated[date, Field(default_factory=date.today)]
"""Date fields that defaults to today's date. Used for a class' entry and update to record time of entry"""


NoEmptyStringMixinExpense = create_string_validators(name="trimmed", description="trimmed")
# ==========================================
# Expense Tables
# ==========================================

class ExpenseBase(SQLModel):
    name: str 
    amount: PositiveAmount
    category_id: int | None = None
    description: str | None = None

class ExpenseCreate(ExpenseBase, NoEmptyStringMixinExpense):
    pass

class ExpenseUpdate(SQLModel, NoEmptyStringMixinExpense):
    name: str | None = None
    amount: Optional[PositiveAmount] = None
    category_id: int | None = None
    description: str | None = None

class Expense(ExpenseBase, table=True):
    expense_id: int | None = Field(primary_key=True, default=None, description="Primary key")
    category_id: int = Field(foreign_key="category.category_id") # type: ignore
    user_id: int = Field(foreign_key="user.user_id")
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None
