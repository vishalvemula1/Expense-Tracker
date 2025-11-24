from pydantic import EmailStr
from .validators import PositiveAmount, create_string_validators
from sqlmodel import Field, SQLModel

USERNAME_REGEX = "^[a-zA-Z0-9_-]+$"


UserWhitespaceTrimmerMixin = create_string_validators("username", "email")

class UserBase(SQLModel):
    username: str = Field(unique=True, index=True, min_length=3, max_length=50, regex=USERNAME_REGEX)
    email: EmailStr = Field(unique=True, index=True, min_length=3, max_length=128)
    salary: PositiveAmount | None

class UserCreate(UserBase, UserWhitespaceTrimmerMixin):
    password: str = Field(min_length=8, max_length=128)

class UserRead(UserBase):
    user_id: int 

class User(UserBase, table=True):
    user_id: int | None = Field(primary_key=True, default=None)
    password_hash: str

class UserUpdate(UserBase, UserWhitespaceTrimmerMixin):
    username: str | None = Field(min_length=3, max_length=50, regex=USERNAME_REGEX, default=None)
    email: EmailStr | None = None
    salary: PositiveAmount | None = None
    password: str | None = Field(min_length=8, max_length=128, default=None)