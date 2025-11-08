from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

class AppExceptions:
    CredentialsException = HTTPException(status_code=401, 
                                      detail="Could not validate credentials",
                                      headers={"WWW-Authenticate": "Bearer"})
    
    InvalidUsernamePassword = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid username or password")

    Unauthorized = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authorized for this request")

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
    
    if "uq_category_name_user" in error_info:
        raise IntegrityExceptions.CategoryNameExists
    
    if "foreign key constraint" in error_info:
        raise IntegrityExceptions.ForeignKeyDoesntExist
    
    import logging
    logging.error(f"Unhandled IntegrityError in {context}: {error_info}")

    raise IntegrityExceptions.UnknownIntegrityError