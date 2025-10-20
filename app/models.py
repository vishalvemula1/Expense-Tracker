from typing import Annotated, Optional
from pydantic import EmailStr
from datetime import date
from sqlmodel import Field, SQLModel

PositiveAmount = Annotated[float, Field(ge= 0, description="Amount must be greater than zero", default=0)]
DateCheck = Annotated[date, Field(default_factory=date.today)]

class UserBase(SQLModel):
    username: str
    email: EmailStr | None = None
    salary: int | None

class UserCreate(UserBase):
    password: str


class UserRead(UserBase):
    user_id: int | None 

class User(UserBase, table=True):
    user_id: int | None = Field(primary_key=True, default=None)
    password_hash: str

class UserUpdate(UserBase):
    username: str | None = None
    email: EmailStr | None = None
    salary: int | None = None
    password: str | None = None



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
    expense_id: int | None = Field(default=None, primary_key=True)
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None
    user_id: int = Field(foreign_key="user.user_id")