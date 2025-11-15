from typing import TypeVar, Type
from fastapi import HTTPException
from sqlmodel import SQLModel, Session



ModelType = TypeVar('ModelType', bound=SQLModel)

def get_object_or_404(model: Type[ModelType], object_id: int, session: Session) -> ModelType:
    object_data = session.get(model, object_id)
    if not object_data:
        raise HTTPException(status_code=404, detail=f"{model.__name__} was not found")
    return object_data
