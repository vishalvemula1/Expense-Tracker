from __future__ import annotations

from ..models import User, Category, CategoryCreate, CategoryUpdate, Expense
from .utils import get_object_or_404
from ..exceptions import db_transaction
from ..dependencies import VerifiedOwnerDep, SessionDep
from ..exceptions import AppExceptions
from sqlmodel import Session, select
from fastapi import HTTPException


class CategoryService:
    def __init__(self, user: User, session: Session) -> None:
        self.user = user
        self.session = session

    def _get_read_category(self, category_id: int | None) -> Category:
        if category_id is None:
            category = self.session.exec(select(Category).where(Category.user_id == self.user.user_id, Category.is_default == True)).first()
            if category is None:
                raise HTTPException(status_code=404, detail="Default category not found")
            return category

        data = get_object_or_404(model=Category, object_id=category_id, session=self.session)
        if data.user_id != self.user.user_id:
            raise AppExceptions.Unauthorized
        return data

    def _get_write_category(self, category_id: int) -> Category:
        category = self._get_read_category(category_id)

        if category.is_default:
            raise AppExceptions.DefaultCategoryUneditable

        return category

    def create(self, new_category: CategoryCreate) -> Category:
        with db_transaction(self.session, context="Category Creation") as db:
            category_data = Category.model_validate(new_category, update={"user_id": self.user.user_id})

            db.add(category_data)
            db.commit()

            db.refresh(category_data)

        return category_data

    def get(self, category_id: int) -> Category:
        return self._get_read_category(category_id)

    def update(self, category_id: int, update_request: CategoryUpdate) -> Category:
        category = self._get_write_category(category_id)

        with db_transaction(self.session, context="Category Update") as db:
            update_data = update_request.model_dump(exclude_unset=True)

            category.sqlmodel_update(update_data)
            
            db.add(category)
            db.commit()

            db.refresh(category)

        return category        
    
    def delete(self, category_id: int) -> None:
        category = self._get_write_category(category_id)

        self.session.delete(category)
        self.session.commit()

    def list(self, limit: int, offset: int) -> list[Category]:
        statement = (select(Category)
        .where(Category.user_id == self.user.user_id)
        .limit(limit)
        .offset(offset))

        data = self.session.exec(statement).all()

        return list(data)

    def get_expenses(self, category_id: int) -> list[Expense]: #type: ignore
        category = self._get_read_category(category_id)

        statement = (select(Expense).where(Expense.category_id == category.category_id))

        data = self.session.exec(statement).all()

        return list(data)    

def get_category_service(user: VerifiedOwnerDep, session: SessionDep) -> CategoryService:
    return CategoryService(user, session)