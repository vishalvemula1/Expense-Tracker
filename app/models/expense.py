from typing import Annotated
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
    amount: PositiveAmount | None = None
    category_id: int | None = None
    description: str | None = None

class ExpenseRead(ExpenseBase):
    expense_id: int
    category_id: int #type: ignore
    date_of_entry: DateCheck
    date_of_update: DateCheck | None

    
class Expense(ExpenseBase, table=True):
    expense_id: int | None = Field(primary_key=True, default=None, description="Primary key")
    category_id: int = Field(foreign_key="category.category_id", index=True, ondelete="CASCADE") # type: ignore
    user_id: int = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")
    date_of_entry: DateCheck
    date_of_update: DateCheck | None = None