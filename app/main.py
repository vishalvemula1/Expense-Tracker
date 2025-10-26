from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .routers.expenses import router as expenses_router
from .routers.users import router as users_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(expenses_router)

app.include_router(users_router)