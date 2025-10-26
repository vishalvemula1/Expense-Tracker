from typing import Annotated, Optional
from pydantic import EmailStr, field_validator
from datetime import date
from sqlmodel import Field, SQLModel



# ==========================================
# Validator Function & Mixins
# ==========================================
def validate_no_empty_strings(v):
    """Strip whitespace and reject empty strings"""
    if v is None:
        return v
    
    if isinstance(v, str):
        v = v.strip()
    
    if isinstance(v, str) and v == "":
        raise ValueError("Cannot be empty or whitespace only")
    
    return v

class NoEmptyStringsMixinUser:
    
    @field_validator("username", "password", "email", mode="before")
    @classmethod
    def validate_user_fields(cls, v):
        return validate_no_empty_strings(v)

class NoEmptyStringsMixinExpense:
    
    @field_validator("name", "category", "description", mode="before")
    @classmethod
    def validate_expense_fields(cls, v):
        return validate_no_empty_strings(v)
    

# ==========================================
# Type Aliases
# ==========================================

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

class UserCreate(UserBase, NoEmptyStringsMixinUser):
    password: str

class UserRead(UserBase):
    user_id: int | None 

class User(UserBase, table=True):
    user_id: int | None = Field(primary_key=True, default=None, description="Primary key")
    password_hash: str

class UserUpdate(UserBase, NoEmptyStringsMixinUser):
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