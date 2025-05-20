"""
This file defines the database models
"""
import datetime

from . common import db, Field, auth
from pydal.validators import *

### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later
#
# db.commit()
#
def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()



db.define_table(
    'product',
    Field('product_name'),
    #Field('product_quantity', 'integer',
    #      requires=IS_INT_IN_RANGE(0, None),
    #      default=0),
    Field('vocabulary', 'integer', default=0),
    Field('active', 'boolean'),
    Field('creation_date', 'datetime', default=get_time),
    Field('flow', default=None)
)
#db.define_table('flow',
#    Field('phone_number'),
#    Field('kind'),
#    Field('contactID', 'reference contacts')
#)
db.define_table('post',
                Field('user_email', default=1),
                Field('post_text', 'text'),
                Field('ts', 'datetime', default=get_time),
                )

db.define_table('thumb',
                Field('user_email', default=get_user_email()),
                Field('post_id', 'reference post'),
                Field('rating', 'integer', default=0)
                )

# We do not want these fields to appear in forms by default.
db.product.id.readable = False
db.product.creation_date.readable = False
db.product.flow.readable = False


db.commit()
