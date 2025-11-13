from sqlmodel import SQLModel, Field
from .validators import create_string_validators
from enum import Enum
from .expense import DateCheck
from sqlalchemy import UniqueConstraint

NoEmptyStringsMixinCategory = create_string_validators(name="trimmed", description="trimmed")

class Color(str, Enum):
    Blue = "Blue"
    Red = "Red"
    Black = "Black"
    White = "White"


class CategoryBase(SQLModel):
    name: str
    description: str | None = None
    tag: Color | None = None


class CategoryCreate(CategoryBase, NoEmptyStringsMixinCategory):
    pass

class CategoryUpdate(CategoryBase, NoEmptyStringsMixinCategory):
    name: str | None = None
    description: str | None = None
    tag: Color | None = None


class CategoryRead(CategoryBase):
    category_id: int
    date_of_entry: DateCheck
    is_default: bool

class Category(CategoryBase, table=True):
    __table_args__ = (UniqueConstraint('name', 'user_id', name='uq_category_name_user'),)
    user_id: int = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")
    category_id: int | None = Field(primary_key=True, default=None)
    date_of_entry: DateCheck
    is_default: bool = False

