from .common import db, Field, auth
from pydal.validators import *
import datetime

db.define_table(
    "bird",
    Field("id", "integer", readable=False, writable=False),
    Field('name', "string", requires=[IS_NOT_EMPTY(), IS_NOT_IN_DB(db, 'bird.name')]),
    Field("habitat", "string", default=""),
    Field("weight", "float", default = 0, requires=IS_FLOAT_IN_RANGE(0, 1000, error_message='Weight must be between 0 and 1000')),
    Field("sightings", "integer", default=0),

)
