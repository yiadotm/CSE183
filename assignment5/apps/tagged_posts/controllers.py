from py4web import action, redirect, URL, request, Field, HTTP
from py4web.utils.form import Form
from .common import flash, session, db, auth
import re
import logging
import json
from flask import jsonify
from datetime import datetime

#
# Convenience functions
#


def check_liked(items):
    """add a liked attributed to each item"""
    query = db.item_like.created_by == auth.user_id
    query &= db.item_like.item_id.belongs([item.id for item in items])
    liked_ids = set(row.item_id for row in db(query).select(db.item_like.item_id))
    for item in items:
        item["liked"] = "true" if item.id in liked_ids else "false"


def friend_ids(user_id):
    """return a list of ids of friends (included user_id self)"""
    query = db.friend_request.status == "accepted"
    query &= (db.friend_request.to_user == user_id) | (
        db.friend_request.from_user == user_id
    )
    rows = db(query).select()
    return (
        set([user_id])
        | set(row.from_user for row in rows)
        | set(row.to_user for row in rows)
    )

def serialize_datetime(obj):
    """JSON serializer for objects not serializable by default"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")
#
# Pages
#


@action("index")
@action.uses("index.html", auth)
def index():
    if auth.user_id:
        redirect(URL("posts"))
    else:
        redirect(URL('auth', 'login'))
    return {}


@action('/tagged_posts/api/posts', method=["GET"])
@action.uses("feed.html", auth.user)
def api_get_posts():
    try:
        # Create a form
        form = Form(db.post_item)

        # Get tags from query parameters
        tags = request.query.get('tags')
        if tags:
            tags = tags.split(',')
            # Retrieve the 100 most recent posts with specified tags
            items = db((db.post_item.id == db.tag_item.post_id) & 
                       (db.tag_item.name.belongs(tags))).select(
                db.post_item.ALL, orderby=~db.post_item.created_on, limitby=(0, 100), distinct=True
            )
        else:
            # Retrieve the 100 most recent posts
            items = db().select(
                db.post_item.ALL, orderby=~db.post_item.created_on, limitby=(0, 100)
            )

        return dict(form=form, items=items)
    except Exception as e:
        return dict(error=str(e), form=form)


@action('/tagged_posts/api/posts', method=["POST"])
@action.uses(auth.user)
def api_post_posts():
    try:
        form = Form(db.post_item)
        logging.info(f"Form data: {form.vars}")
        if form.accepted:
            post_id = form.vars['id']
            tags = re.findall(r"#(\w+)", form.vars['content'])
            for tag in tags:
                db.tag_item.insert(name=tag, post_item_id=post_id)
            # Retrieve the new post from the database
            new_post = db(db.post_item.id == post_id).select().first().as_dict()
            # redirect(URL('/tagged_posts/api/posts'))
            return new_post
        elif form.errors:
            logging.error(f"Form errors: {form.errors}")
            return dict(error=form.errors)
        return {'id': form.vars.get('id', ''), 'content': form.vars.get('content', '')}
    except Exception as e:
        logging.error(f"Exception: {str(e)}")
        return dict(error=str(e))

@action('/tagged_posts/api/tags', method=["GET"])
@action.uses("feed.html", auth.user)
def api_posts():
    # Retrieve all posts
    items = db(db.post_item).select(db.post_item.ALL, orderby=db.post_item.created_on)
    return dict(items=items) 




@action('/tagged_posts/api/posts/<post_item_id>', method=['DELETE'])
@action.uses(auth.user)
def delete_post(post_item_id):
    try:
        # Check if the user is the author of the post
        post = db.post_item[post_item_id]
        if post.created_by != auth.current_user()['id']:
            raise HTTP(403, 'Only the author can delete the post')

        # Delete the post
        db(db.post_item.id == post_item_id).delete()

        return '', 204  # Return a 204 No Content status code
    except Exception as e:
        return dict(error=str(e)), 500  # Return a 500 Internal Server Error status code
    

@action("posts", method=["GET", "POST"])
@action.uses("feed.html", auth.user)
def feed():
    # make up some random data if only one user

    # a form to post a new item to the feed
    form = Form(db.feed_item)
    # list of 100 most recent posted items by user or friends
    items = db(db.feed_item.created_by.belongs(friend_ids(auth.user_id))).select(
        orderby=~db.feed_item.created_on, limitby=(0, 100)
    )
    # determine if they were liked or not
    check_liked(items)

    return locals()


# @action("home/<user_id:int>", method=["GET", "POST"])
# @action.uses("home.html", auth.user)
# def home(user_id):
#     if user_id not in friend_ids(auth.user_id):
#         raise HTTP(400)
#     user = db.auth_user(user_id)
#     # list of recent items posted by the user
#     items = db(db.feed_item.created_by == user_id).select(
#         orderby=~db.feed_item.created_on, limitby=(0, 100)
#     )
#     # determine if they were liked or not
#     check_liked(items)
#     return locals()


# @action("friends", method=["GET", "POST"])
# @action.uses("friends.html", auth.user)
# def friends():
#     # a search form (simply by first name)
#     form = Form([Field("name", required=True)])
#     users = []
#     if form.accepted:
#         # select users based on the tokens in the search input
#         query = None
#         for token in form.vars.get("name").split():
#             q = db.auth_user.first_name.lower().startswith(
#                 token.lower()
#             ) | db.auth_user.last_name.lower().startswith(token.lower())
#             query = query & q if query else q
#         if query:
#             users = db(query).select()

#     # make list of requests
#     alphabetical = db.auth_user.first_name + db.auth_user.last_name
#     query_received = (db.friend_request.to_user == auth.user_id) & (
#         db.friend_request.from_user == db.auth_user.id
#     )
#     requests_received = db(query_received).select(orderby=alphabetical)
#     # make list of requests sent
#     query_sent = (db.friend_request.from_user == auth.user_id) & (
#         db.friend_request.to_user == db.auth_user.id
#     )
#     requests_sent = db(query_sent).select(orderby=alphabetical)

#     # return the form, lists, and button factories
#     return locals()


# #
# # Callback actions
# #


# @action("like/<item_id:int>", method=["POST"])
# @action.uses(auth.user)
# def like(item_id):
#     # try unlike
#     if db(db.item_like.item_id == item_id).delete():
#         return dict(liked=False)
#     # else like
#     db.item_like.insert(item_id=item_id)
#     return dict(liked=True)


# @action("friendship/request/<user_id:int>", method=["POST"])
# @action.uses(auth.user)
# def friendship_request(user_id):
#     # if request does not exist already, create it
#     query = (db.friend_request.to_user == user_id) & (
#         db.friend_request.from_user == auth.user_id
#     )
#     query |= (db.friend_request.to_user == auth.user_id) & (
#         db.friend_request.from_user == user_id
#     )
#     if not db(query).count():
#         db.friend_request.insert(
#             from_user=auth.user_id, to_user=user_id, status="pending"
#         )


# @action("friendship/<id:int>/accept", method=["POST"])
# @action.uses(auth.user)
# def friendship_accept(id):
#     # the target user can accept the request
#     db(
#         (db.friend_request.id == id) & (db.friend_request.to_user == auth.user_id)
#     ).update(status="accepted")


# # make a button factory to reject frindship
# @action("friendship/<id:int>/reject", method=["POST"])
# @action.uses(auth.user)
# def friendship_reject(id):
#     # both origin and target users can delete a request
#     db(db.friend_request.id == id).delete()
