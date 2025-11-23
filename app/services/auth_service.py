from ..models import User, UserCreate, Category, Token
from ..exceptions import db_transaction
from ..security import get_password_hash
from ..config import default_categories as defaults
from datetime import date
from sqlmodel import Session
from fastapi.security import OAuth2PasswordRequestForm
from ..auth import authenticate_user, create_token
from ..dependencies import SessionDep

class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session


    def create_user_with_defaults(self, user: UserCreate) -> User:
        with db_transaction(self.session, context="User Signup") as db:
            hashed_password = get_password_hash(user.password)
        user = authenticate_user(form_data.username, form_data.password, self.session)

        token = create_token(user.user_id) #type: ignore

        return Token(access_token=token, token_type="bearer")
    
def get_auth_service(session: SessionDep) -> AuthService:
    return AuthService(session)


        