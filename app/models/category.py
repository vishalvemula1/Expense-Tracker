from sqlmodel import SQLModel, Field
from .validators import create_non_empty_validator_mixin
from enum import Enum
from .expense import DateCheck

NoEmptyStringsMixinCategory = create_non_empty_validator_mixin("name", "description")

class Color(str, Enum):
    Blue = "Blue"
    Red = "Red"
    Black = "Black"
    White = "White"


class CategoryBase(SQLModel):
    name: str = Field(unique=True)
    description: str | None = None
    tag: Color | None = None


class CategoryCreate(CategoryBase, NoEmptyStringsMixinCategory):
    pass

class CategoryUpdate(CategoryBase, NoEmptyStringsMixinCategory):
    name: str | None = None
    description: str | None = None
    tag: Color | None = None

class Category(CategoryBase, table=True):
    user_id: int = Field(foreign_key="user.user_id")
    category_id: int | None = Field(primary_key=True, default=None)
    date_of_entry: DateCheck

