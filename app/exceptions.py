from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from contextlib import contextmanager
from sqlmodel import Session


class AppExceptions:
    CredentialsException = HTTPException(status_code=401, 
                                      detail="Could not validate credentials",
                                      headers={"WWW-Authenticate": "Bearer"})
    
    InvalidUsernamePassword = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    Unauthorized = HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized for this request")

    DefaultCategoryUneditable = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Not allowed to edit or delete default category") 


class IntegrityExceptions:
    ForeignKeyDoesntExist = HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reference: the referenced resource does not exist")

    UnknownIntegrityError = HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="A database constraint was violated")

    UserExists = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Username already exists")

    EmailExists = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already exists")

    CategoryNameExists = HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category with the same name already exists")



def handle_integrity_error(e: IntegrityError, context: str = ""):
    
    error_info = str(e.orig).lower()

    if "user.username" in error_info:
        raise IntegrityExceptions.UserExists
    
    if "user.email" in error_info:
        raise IntegrityExceptions.EmailExists
    
    if "uq_category_name_user" in error_info or "category.name, category.user_id" in error_info:
        raise IntegrityExceptions.CategoryNameExists
    
    if "foreign key constraint" in error_info:
        raise IntegrityExceptions.ForeignKeyDoesntExist
    
    import logging
    logging.error(f"Unhandled IntegrityError in {context}: {error_info}")

    raise IntegrityExceptions.UnknownIntegrityError

@contextmanager
def db_transaction(session: Session, context: str = ""):
    """Context manager for database transactions with automatic IntegrityError handling.
    
    Usage:
        with db_transaction(session, "User Creation") as db:
            db.add(user)
            db.commit()
    
    On IntegrityError, automatically rolls back and raises appropriate HTTPException.
    """
    try:
        yield session
    
    except IntegrityError as e:
        session.rollback()
        handle_integrity_error(e, context=context)
    
    except Exception:
        session.rollback()
        raise