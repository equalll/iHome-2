from . import api
from flask import session
import logging
from iHome import redis_store

@api.route("/index",methods=["GET","POST"])
def index():
    session["name"] ="xiaohua"
    logging.debug('DEBUG')
    redis_store.set('name','xiaoruirui')
    return "index2"