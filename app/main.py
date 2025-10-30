from fastapi import FastAPI
from contextlib import asynccontextmanager
from .database import create_db_and_tables
from .routers import expenses_router
from .routers import users_router
from .routers import categories_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(expenses_router)

app.include_router(users_router)

app.include_router(categories_router)