from typing import Annotated, Optional
from .validators import create_non_empty_validator_mixin
from datetime import date
from sqlmodel import Field, SQLModel
from .user import PositiveAmount


DateCheck = Annotated[date, Field(default_factory=date.today)]
NoEmptyStringsMixinExpense = create_non_empty_validator_mixin("name", "category", "description")
# ==========================================
# Expense Tables
# ==========================================

class ExpenseBase(SQLModel):
    name: str 
    amount: PositiveAmount
    category: str | None = None
    description: str | None = None

class ExpenseCreate(ExpenseBase, NoEmptyStringsMixinExpense):
    pass

class ExpenseUpdate(ExpenseBase, NoEmptyStringsMixinExpense):
    name: str | None = None
    amount: Optional[PositiveAmount] = None
    category: str | None = None
    description: str | None = None

class Expense(ExpenseBase, table=True):
    expense_id: int | None = Field(primary_key=True, default=None, description="Primary key")
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None
    user_id: int = Field(foreign_key="user.user_id")