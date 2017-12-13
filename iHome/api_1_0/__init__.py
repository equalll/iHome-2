# -*- coding:utf-8 -*-
from flask import Blueprint

#new a api's blueprint
api=Blueprint("api_1_0", __name__)

from . import verify
from . import passport
from . import house
from . import profile,order
