from fastapi import Query, APIRouter, Depends
from typing import Annotated
from ..models import Category, CategoryCreate, CategoryUpdate, Expense, CategoryRead, ExpenseRead
from ..services import CategoryService, get_category_service

category_router = APIRouter(prefix="/me/categories", tags=["categories"])

CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]

@category_router.post("/", response_model=CategoryRead)
async def create_category(svc: CategoryServiceDep,
                          new_category: CategoryCreate) -> Category:

    return svc.create(new_category)

@category_router.get("/{category_id}", response_model=CategoryRead)
async def get_category(svc: CategoryServiceDep,
                       category_id: int) -> Category:

    return svc.get(category_id)

@category_router.put("/{category_id}", response_model=CategoryRead)
async def update_category(svc: CategoryServiceDep,
                          category_id: int,
                          update_request: CategoryUpdate) -> Category:

    return svc.update(category_id, update_request)

@category_router.delete("/{category_id}")
async def delete_category(svc: CategoryServiceDep,
                          category_id: int):

    svc.delete(category_id)

@category_router.get("/", response_model=list[CategoryRead])
async def list_categories(svc: CategoryServiceDep,
                          limit: Annotated[int, Query(le=100)] = 5,
                          offset: int = 0) -> list[Category]:

    return svc.list(limit, offset)

@category_router.get("/{category_id}/expenses", response_model=list[ExpenseRead])
async def get_category_expenses(svc: CategoryServiceDep,
                                category_id: int) -> list[Expense]:

    return svc.get_expenses(category_id)