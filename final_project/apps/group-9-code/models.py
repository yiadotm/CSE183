# models.py

from pydal.validators import IS_IN_SET, IS_NOT_EMPTY, IS_EMAIL, IS_NOT_IN_DB
from .common import Field, auth, db
from py4web.utils.auth import Auth
from py4web import DAL, Field, Session, Cache
from py4web.utils.auth import Auth
import datetime



def get_user_id():
    return auth.current_user.get('id') if auth.current_user else None

def get_user_firstname():
    return auth.current_user.get('first_name') if auth.current_user else None

# Define the roles
ROLES = ['CEO', 'Manager', 'User']

# Define user extension table for roles and manager_id
db.define_table('user_extension',
    Field('user_id', 'reference auth_user'),
    Field('role', default='User'),
    Field('manager_id', 'reference auth_user', default=1)  # Default manager is CEO
)


# Set user ID 1 to CEO if not already set
user_extension = db(db.user_extension.user_id == 1).select().first()
if not user_extension:
    db.user_extension.insert(user_id=1, role='CEO', manager_id=1)
elif user_extension.role != 'CEO':
    user_extension.update_record(role='CEO')
    db.commit()


# Define the 'tasks' table
db.define_table(
    "tasks",
    Field("name", requires=IS_NOT_EMPTY()),
    Field("description", "text", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False, readable=False),
    Field("deadline", "datetime"),
    Field("completed", "boolean", default=False, writable=False, readable=False),
)

# Define the 'assigned' table
db.define_table(
    "assigned",
    Field("asignee", "reference auth_user"),
    Field("task_id", "reference tasks")
)

# Define the 'comments' table
db.define_table(
    "comments",
    Field("text", "text", requires=IS_NOT_EMPTY()),
    Field("user_id", "reference auth_user", default=get_user_id, writable=False, readable=False),
    Field("task_id", "reference tasks"),
    Field("created_on", "datetime", default=datetime.datetime.utcnow)
)

db.commit()
