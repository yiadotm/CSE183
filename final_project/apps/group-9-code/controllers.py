# controllers.py

import datetime
import logging

from py4web import URL, action, request
from py4web.utils.url_signer import URLSigner
from yatl.helpers import A

from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated
from .models import get_user_id, get_user_firstname

url_signer = URLSigner(session)

def get_assigned_users(task_id):
    assignees_ids = db((db.assigned.task_id == task_id)).select(db.assigned.asignee).as_list()
    assignees_names = []
    for user in assignees_ids:
        if 'asignee' in user:
            if db.auth_user[user['asignee']].first_name == get_user_firstname():
                assignees_names.append("You")
            else:
                assignees_names.append(db.auth_user[user['asignee']].first_name)
    return assignees_names

@action("index")
@action.uses("index.html", auth.user, db, url_signer)
def index():
    return dict(
        get_tasks_url=URL('get_tasks', signer=url_signer),
        get_users_url=URL('get_users', signer=url_signer),
        complete_task_url=URL('complete_task', signer=url_signer),
        edit_url=URL('edit', signer=url_signer),
        add_url=URL('add', signer=url_signer),
        save_comment_url=URL('save_comment', signer=url_signer),
        get_comments_url=URL('get_comments', signer=url_signer),
        delete_comment_url=URL('delete_comment', signer=url_signer),
        assign_role_url=URL('assign_role', signer=url_signer),
        get_user_url=URL('get_user', signer=url_signer),
        update_user_role_url=URL('update_user_role', signer=url_signer),
        update_manager_id_url=URL('update_manager_id', signer=url_signer),
    )

@action("get_tasks", method="GET")
@action.uses(db, auth.user)
def get_tasks():
    user_id = get_user_id()
    user_tasks = db((db.tasks.user_id == user_id)).select(db.tasks.ALL).as_list()
    assigned_tasks = db((db.assigned.asignee == user_id) & (db.tasks.id == db.assigned.task_id)).select(db.tasks.ALL).as_list()

    uncompleted_tasks = [t for t in user_tasks if t['completed'] == False] + [t for t in assigned_tasks if t['completed'] == False]
    completed_tasks = [t for t in user_tasks if t['completed'] == True] + [t for t in assigned_tasks if t['completed'] == True]

    for r in uncompleted_tasks:
        r['timeleft'] = r['deadline'].isoformat()
        r['overdue'] = datetime.datetime.now() > r['deadline'] + datetime.timedelta(hours=7)
        r['assigned'] = get_assigned_users(r['id'])
        r['comments'] = db(db.comments.task_id == r['id']).select().as_list()

    for r in completed_tasks:
        r['assigned'] = get_assigned_users(r['id'])
        r['comments'] = db(db.comments.task_id == r['id']).select().as_list()

    return dict(completed=completed_tasks, uncompleted=uncompleted_tasks)

@action('add', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def add():
    name = request.json.get('name')
    description = request.json.get('description')
    deadline_str = request.json.get('deadline')
    assigned = request.json.get('assigned')

    if deadline_str:
        deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
    else:
        deadline = datetime.datetime.now()

    new_task = db.tasks.insert(name=name, description=description, deadline=deadline)
    for user in assigned:
        db.assigned.insert(asignee=user, task_id=new_task)
    
    return "ok"

@action('edit', method="POST")
@action.uses(db, auth.user, url_signer.verify())
def edit():
    id = request.json.get('task_id')
    name = request.json.get('name')
    description = request.json.get('description')
    deadline_str = request.json.get('deadline')
    assigned = request.json.get('assigned')

    if deadline_str:
        try:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            deadline = datetime.datetime.strptime(deadline_str, '%Y-%m-%d %H:%M:%S')
    else:
        deadline = datetime.datetime.now()

    new_task = {
        'name': name,
        'description': description,
        'deadline': deadline,
    }

    db(db.tasks.id == id).update(**new_task)
    
    add = list(set(assigned[0]) - (set(assigned[0]) & set(assigned[1])))
    remove = list(set(assigned[1]) - (set(assigned[0]) & set(assigned[1])))

    for user in add:
        db.assigned.insert(asignee=user, task_id=id)
    for user in remove:
        db((db.assigned.task_id == id) & (db.assigned.asignee == user)).delete()

    return "ok"

@action("complete_task", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def complete_task():
    id = request.json.get('task_id')
    t = db.tasks[id]

    assginees = db((db.assigned.task_id == t)).select(db.assigned.asignee).as_list()
    assginee_ids = [a['asignee'] for a in assginees if 'asignee' in a]
    assginee_ids.append(t.user_id)

    if get_user_id() in assginee_ids:
        status = db(db.tasks.id == t.id).select()[0]
        db(db.tasks.id == t.id).update(completed=not status.completed)
    return "ok"


@action("get_users", method="GET")
@action.uses(db, auth.user)
def get_users():
    users = db(db.auth_user).select().as_list()
    logging.info(f"User IDs: {[user['id'] for user in users]}")
    return dict(users=users) 


@action("save_comment", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def save_comment():
    text = request.json.get('comment')['text']
    task_id = request.json.get('comment')['task_id']
    db.comments.insert(text=text, task_id=task_id, user_id=get_user_id())
    return dict(success=True)

@action("get_comments", method="GET")
@action.uses(db, auth.user)
def get_comments():
    return dict(comments=db(db.comments).select().as_list())

@action("delete_comment", method="POST")
@action.uses(db, auth.user, url_signer.verify())
def delete_comment():
    comment_id = request.json.get('comment_id')
    db(db.comments.id == comment_id).delete()
    return dict(success=True)

@action('update_status', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def update_status():
    task_id = request.json.get('task_id')
    status = request.json.get('status')
    db(db.tasks.id == task_id).update(status=status)
    return dict(success=True)



@action('get_user/<user_id:int>', method=['GET'])
@action.uses(auth.user, db)
def get_user(user_id):
    try:
        logger.info(f"Fetching user with ID: {user_id}")
        user = db.auth_user(user_id)
        if not user:
            logger.error(f"User with ID {user_id} not found")
            return {"error": "User not found"}
        user_ext = db(db.user_extension.user_id == user_id).select().first()
        if not user_ext:
            # Create an entry in user_extension if it does not exist
            user_ext_id = db.user_extension.insert(user_id=user_id, role='User', manager_id=1)
            user_ext = db.user_extension(user_ext_id)
        if not user_ext.manager_id:
            user_ext.update_record(manager_id=1)
        logger.info(f"Fetched user data: {user}")
        logger.info(f"User role: {user_ext.role}")
        logger.info(f"User manager ID: {user_ext.manager_id}")
        return {"user": user, "manager_id": user_ext.manager_id, "role": user_ext.role}
    except Exception as e:
        logger.error(f"Error fetching user with ID {user_id}: {e}")
        return {"error": "Internal server error"}

@action('update_user_role', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def update_user_role():
    user_id = request.json.get('user_id')
    role = request.json.get('role')

    # Log the incoming request data
    logger.info(f"Received data: user_id={user_id}, role={role}")

    if not user_id or not role:
        logger.error("Invalid input")
        return dict(success=False, message="Invalid input")

    # Check if there is already a CEO
    if role == "CEO" and db(db.user_extension.role == "CEO").count() > 0:
        logger.error("There can only be one CEO.")
        return dict(success=False, message="There can only be one CEO.")

    try:
        # Update the user role
        db(db.user_extension.user_id == user_id).update(role=role)
        logger.info("Role updated successfully")
        return dict(success=True)
    except Exception as e:
        # Log the exception details
        logger.error(f"Error updating role: {e}")
        return dict(success=False, message="Error updating role")








@action('update_manager_id', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def update_manager_id():
    user_id = request.json.get('user_id')
    manager_id = request.json.get('manager_id')

    logger.info(f"Received data: user_id={user_id}, manager_id={manager_id}")

    if not user_id or manager_id is None:
        logger.error("Invalid input")
        return dict(success=False, message="Invalid input")

    # Check for circular management
    managed_users = [user.user_id for user in db(db.user_extension.manager_id == user_id).select()]
    if manager_id in managed_users:
        logger.error("Circular management hierarchy detected.")
        return dict(success=False, message="Circular management hierarchy detected.")

    db(db.user_extension.user_id == user_id).update(manager_id=manager_id)
    logger.info("Manager ID updated successfully")
    return dict(success=True)







    
# @action('update_user_role', method='POST')
# @action.uses(db, auth.user, url_signer.verify())
# def update_user_role():
#     user_id = request.json.get('user_id')
#     role = request.json.get('role')
#     manager_id = request.json.get('manager_id')

#     logger.info(f"Received data: user_id={user_id}, role={role}, manager_id={manager_id}")

#     if not user_id or not role or manager_id is None:
#         logger.error("Invalid input")
#         return dict(success=False, message="Invalid input")

#     if role == "CEO" and db(db.user_extension.role == "CEO").count() > 0:
#         logger.error("There can only be one CEO.")
#         return dict(success=False, message="There can only be one CEO.")
    
#     # Check for circular management
#     if role == "Manager":
#         managed_users = [user.user_id for user in db(db.user_extension.manager_id == user_id).select()]
#         if manager_id in managed_users:
#             logger.error("Circular management hierarchy detected.")
#             return dict(success=False, message="Circular management hierarchy detected.")

#     db(db.user_extension.user_id == user_id).update(role=role, manager_id=manager_id)
#     logger.info("Role and manager updated successfully")
#     return dict(success=True)




# @action('remove_role', method=['POST'])
# @action.uses(auth.user, db)
# def remove_role():
#     user_id = request.json.get('user_id')
#     role = request.json.get('role')
#     if not user_id or not role:
#         return {"error": "Invalid input"}

#     roles.remove(user_id, role)
#     return {"message": "Role removed"}


# @action("update_existing_users", method="GET")
# @action.uses(db)
# def update_existing_users():
#     db(db.auth_user.role == None).update(role='User')
#     return "Updated existing users"
