from sqlmodel import create_engine, SQLModel, Session
from .config import settings
from typing import Annotated
from fastapi import Depends

sqlite_file_name = "database.db"
sqlite_url = settings.DATABASE_URL


connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args = connect_args)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]