from ..models import User, Expense, ExpenseCreate, ExpenseUpdate
from .utils import get_object_or_404
from ..exceptions import db_transaction
from ..dependencies import VerifiedOwnerDep, SessionDep
from ..exceptions import AppExceptions
from .category_service import CategoryService
from datetime import date
from sqlmodel import Session, select
from typing import Annotated
from fastapi import Query

class ExpenseService:
    def __init__(self, user: User, session: Session) -> None:
        self.user = user
        self.session = session

    def _get_expense(self, expense_id: int) -> Expense:
        data = get_object_or_404(model=Expense, object_id=expense_id, session=self.session)
        if data.user_id != self.user.user_id:
            raise AppExceptions.Unauthorized
        return data

    def get(self, expense_id: int) -> Expense:
        return self._get_expense(expense_id)

    def create(self, new_expense: ExpenseCreate) -> Expense:
        with db_transaction(self.session, context="Expense Creation") as db:
            category_service = CategoryService(self.user, db)
            category = category_service._get_read_category(new_expense.category_id)

            expense_data = Expense.model_validate(new_expense, update={"user_id": self.user.user_id, "category_id": category.category_id})

            db.add(expense_data)
            db.commit()

            db.refresh(expense_data)

        return expense_data

    def list(self, limit: Annotated[int, Query(le=100)] = 5,
             offset: int = 0) -> list[Expense]:

        expenses = self.session.exec(
            select(Expense)
            .where(Expense.user_id == self.user.user_id)
            .limit(limit)
            .offset(offset)
            ).all()

        return list(expenses)

    def delete(self, expense_id: int) -> None:
        expense = self._get_expense(expense_id)

        self.session.delete(expense)
        self.session.commit()

    def update(self, expense_id: int, update_request: ExpenseUpdate) -> Expense:
        expense = self._get_expense(expense_id)

        with db_transaction(self.session, context="Expense Update") as db:
            category_service = CategoryService(self.user, db)
            category = category_service._get_read_category(update_request.category_id)

            update_data = update_request.model_dump(exclude_unset=True)
            update_data.update({"category_id": category.category_id})

            expense.sqlmodel_update(update_data)
            expense.date_of_update = date.today()

            db.add(expense)
            db.commit()

            db.refresh(expense)

        return expense

def get_expense_service(user: VerifiedOwnerDep, session: SessionDep) -> ExpenseService:
    return ExpenseService(user, session)

       
    