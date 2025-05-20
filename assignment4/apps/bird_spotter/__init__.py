# check compatibility
import py4web

assert py4web.check_compatible("0.1.20190709.1")

# by importing db you expose it to the _dashboard/dbadmin
from .models import db

# # by importing controllers you expose the actions defined in it
from . import controllers
# from py4web import action

# @action("index")
# def index():
#     return "hello world"
