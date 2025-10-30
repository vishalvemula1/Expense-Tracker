from typing import Annotated, Optional
from pydantic import EmailStr
from .validators import create_string_validators
from sqlmodel import Field, SQLModel

PositiveAmount = Annotated[float, Field(ge=0, description="Amount must be greater than zero", default=0)]
NoEmptyStringsMixinUser = create_string_validators(username="strict", email="trimmed", password="trimmed")

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