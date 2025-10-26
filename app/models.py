from typing import Annotated, Optional
from pydantic import EmailStr
from datetime import date
from sqlmodel import Field, SQLModel

PositiveAmount = Annotated[float, Field(ge=0, description="Amount must be greater than zero", default=0)]
# ==========================================
# Token Class
# ==========================================
class Token(SQLModel):
    access_token: str
    token_type: str

# ==========================================
# User Tables
# ==========================================
class UserBase(SQLModel):
    username: str = Field(unique=True, description="Username must be unique")
    email: EmailStr = Field(unique=True, description="Email must be unique and have an @")
    salary: PositiveAmount | None

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    user_id: int | None 

class User(UserBase, table=True):
    user_id: int | None = Field(primary_key=True, default=None, description="Primary key")
    password_hash: str

class UserUpdate(UserBase):
    username: str = Field(unique=True, description="Username must be unique", default=None)
    email: EmailStr = Field(unique=True, description="Email must be unique and have an @", default=None)
    salary: Optional[PositiveAmount] = None
    password: str | None = None

# ==========================================
# Expense Tables
# ==========================================
#------Aliases-----------
DateCheck = Annotated[date, Field(default_factory=date.today)]
#-----------------------
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
    expense_id: int | None = Field(primary_key=True, default=None, description="Primary key")
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None
    user_id: int = Field(foreign_key="user.user_id")