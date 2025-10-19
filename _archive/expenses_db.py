from fastapi import FastAPI, HTTPException, Depends, Query
from typing import Annotated, Optional, TypeVar, Type
from datetime import date
from sqlmodel import create_engine, SQLModel, select, Session, Field


#Boilerplate for database
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"


connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args = connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

#ALIASES
SessionDep = Annotated[Session, Depends(get_session)]
PositiveAmount = Annotated[float, Field(ge= 0, description="Amount must be greater than zero", default=0)]
DateCheck = Annotated[date, Field(default_factory=date.today)]

#Databases
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
    id: int | None = Field(default=None, primary_key=True)
    date_of_entry: DateCheck
    date_of_update: Optional[DateCheck] = None


#DEPENDENCIES
ModelType = TypeVar('ModelType', bound=SQLModel)

def get_object_or_404(model: Type[ModelType], object_id: int, session: SessionDep):
    object_data = session.get(model, object_id)
    if not object_data:
        raise HTTPException(status_code=404, detail=f"{model.__name__} was not found")
    return object_data

def expense_dependency(expense_id: int, session: SessionDep):
    return get_object_or_404(model=Expense, object_id=expense_id, session=session)

ExpenseDep = Annotated[Expense, Depends(expense_dependency)]

# CRUD OPERATIONS

@app.get("/expenses/{expense_id}")
async def read_an_expense(expense: ExpenseDep):
    return expense

@app.post("/expenses/")
async def add_expense(expense: ExpenseCreate, session: SessionDep):
    expense_data = Expense.model_validate(expense)

    session.add(expense_data)
    session.commit()
    session.refresh(expense_data)

    return expense_data

@app.get("/expenses/")
async def read_expenses(session: SessionDep, 
                        limit: Annotated[int, Query(le=100)] = 5,
                        offset: int = 0) -> list[Expense]:
    
    expenses = session.exec(select(Expense).limit(limit).offset(offset)).all()
    return list(expenses)

@app.delete("/expenses/{expense_id}")
async def delete_expense(expense: ExpenseDep, session: SessionDep):
    expense_data = Expense.model_validate(expense)

    session.delete(expense_data)
    session.commit()

    return expense_data

@app.put("/expenses/{expense_id}")
async def update_expense(expense: ExpenseDep, update_request: ExpenseUpdate, session: SessionDep):
    update_data = update_request.model_dump(exclude_unset=True)
    expense.sqlmodel_update(update_data)
    expense.date_of_update = date.today()
    session.add(expense)
    session.commit()
    session.refresh(expense)
    return expense
