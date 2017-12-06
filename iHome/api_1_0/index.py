from . import api
from flask import session
from iHome import redis_store

@api.route("/index",methods=["GET","POST"])
def index():
    session["name"] ="xiaohua"

    redis_store.set('name','xiaoruirui')
    return "index2"