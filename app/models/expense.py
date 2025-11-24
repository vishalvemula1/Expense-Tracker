from .validators import PositiveAmount, DateCheck, SmallText, LongText
from sqlmodel import Field, SQLModel



class ExpenseBase(SQLModel):
    name: SmallText 
    amount: PositiveAmount
    category_id: int | None = None
    description: LongText | None = None

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(SQLModel):
    name: SmallText | None = None
    amount: PositiveAmount | None = None
    category_id: int | None = None
    description: LongText | None = None

class ExpenseRead(ExpenseBase):
    expense_id: int
    category_id: int #type: ignore
    date_of_entry: DateCheck
    date_of_update: DateCheck | None

    
class Expense(ExpenseBase, table=True):
    expense_id: int | None = Field(primary_key=True, default=None)
    category_id: int = Field(foreign_key="category.category_id", index=True, ondelete="CASCADE") # type: ignore
    user_id: int = Field(foreign_key="user.user_id", index=True, ondelete="CASCADE")
    date_of_entry: DateCheck
    date_of_update: DateCheck | None = None