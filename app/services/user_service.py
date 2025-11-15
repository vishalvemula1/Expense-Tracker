from sqlmodel import Session
from ..dependencies import VerifiedOwnerDep, SessionDep
from ..exceptions import db_transaction
from ..models import User, UserUpdate
from ..security import get_password_hash
from .utils import get_object_or_404

class UserService:
    def __init__(self, user: User, session: Session) -> None:
        self.session = session
        self.user = user

    @staticmethod
    def get_user(user_id: int, session: Session) -> User:
        return get_object_or_404(model=User, object_id=user_id, session=session)

    def get(self) -> User:
        return self.user

    def update(self, update_request: UserUpdate) -> User:
        with db_transaction(self.session, context="User Update") as db:
            update_dict = update_request.model_dump(exclude_unset=True, exclude={"password"})

            if update_request.password:
                hashed_password = get_password_hash(update_request.password)
                update_dict['password_hash'] = hashed_password

            self.user.sqlmodel_update(update_dict)

            db.add(self.user)
            db.commit()

            db.refresh(self.user)

        return self.user

    def delete(self) -> None:
        self.session.delete(self.user)
        self.session.commit()
    
def get_user_service(user: VerifiedOwnerDep, session: SessionDep) -> UserService:
    return UserService(user, session)