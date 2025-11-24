from sqlmodel import SQLModel, Field
from .validators import DateCheck, LongText, SmallText
from enum import Enum
from sqlalchemy import UniqueConstraint, Index, text


class Color(str, Enum):
    Blue = "Blue"
    Red = "Red"
    Black = "Black"
    White = "White"


class CategoryBase(SQLModel):
    name: SmallText
    description: LongText | None = None
    tag: Color | None = None


class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    name: SmallText | None = None
    description: LongText | None = None
    tag: Color | None = None


class CategoryRead(CategoryBase):
    category_id: int
    date_of_entry: DateCheck
    is_default: bool

class Category(CategoryBase, table=True):
    __table_args__ = (
        # Unique category name per user
        UniqueConstraint('name', 'user_id', name='uq_category_name_user'),
        
        # Partial unique index: only one default category per user (WHERE is_default = True)
        Index(
            'uq_one_default_per_user',
            'user_id',
            'is_default',
            unique=True,
            sqlite_where=text('is_default = 1')
        ),
    )
    user_id: int = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")
    category_id: int | None = Field(primary_key=True, default=None)
    date_of_entry: DateCheck
    is_default: bool = False

