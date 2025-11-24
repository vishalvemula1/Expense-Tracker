from sqlalchemy import event
from .user import User
from .category import Category
from ..config import default_categories as defaults
from datetime import date
from ..exceptions import AppExceptions

# ==============================================================================
# Event Listeners
# ==============================================================================
# These listeners enforce business logic at the database/ORM level.
# This ensures that rules are applied regardless of which service or script
# modifies the data, making the system more robust and less prone to errors.

@event.listens_for(User, 'after_insert')
def create_default_category(mapper, connection, target):
    """
    Automatically creates a default 'Uncategorized' category when a new user is created.
    """
    category_table = Category.__table__ #type: ignore
    
    connection.execute(
        category_table.insert().values(
            name=defaults.DEFAULT_CATEGORY_NAME,
            description=defaults.DEFAULT_CATEGORY_DESCRIPTION,
            tag=defaults.DEFAULT_CATEGORY_TAG,
            user_id=target.user_id,
            date_of_entry=date.today(),
            is_default=True
        )
    )

@event.listens_for(Category, 'before_update')
def prevent_default_category_modification(mapper, connection, target):
    if target.is_default:
        raise AppExceptions.DefaultCategoryUneditable

@event.listens_for(Category, 'before_delete')
def prevent_default_category_deletion(mapper, connection, target):
    if target.is_default:
        raise AppExceptions.DefaultCategoryUneditable
