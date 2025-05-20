from .common import *
from pydal.validators import IS_NOT_EMPTY
from py4web import action, redirect, URL, request, Field, HTTP

db.define_table(
    "feed_item", Field("body", "text", requires=IS_NOT_EMPTY()), auth.signature
)

db.define_table("item_like", Field("item_id", "reference feed_item"), auth.signature)

db.define_table(
    "friend_request",
    Field("from_user", "reference auth_user"),
    Field("to_user", "reference auth_user"),
    Field("status", options=("accepted", "pending", "rejected")),
)

db.define_table(
    "post_item",
    Field("content", "text", requires=IS_NOT_EMPTY()),
    # Field("created_on", "datetime", default=request.now),

    auth.signature
)

db.define_table(
    "tag_item",
    Field("name", "string", requires=IS_NOT_EMPTY()),
    Field("post_item_id", "reference post_item"),
    auth.signature
)

db.commit()
