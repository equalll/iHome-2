# -*- coding:utf-8 -*-
import functools

from flask import g
from flask import session, jsonify
from werkzeug.routing import BaseConverter

from iHome.utils.response_code import RET


class RegexConverter(BaseConverter):
    """自定义的正则转换器"""

    def __init__(self,url_map,*args):
        super(RegexConverter, self).__init__(url_map)
        self.regex = args[0]


    # 被装饰器装饰的函数，默认会更改其__name__属性

def login_required(f):
    # 被装饰器装饰的函数，默认会更改其__name__属性
    @functools.wraps(f)
    # 防止装饰器去装饰函数的时候，被装饰的函数__name__属性被更改的问题
    def wrap(*args,**kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(errno=RET.SESSIONERR, errmsg="用户未登录")
        else:
            g.user_id=user_id
            # 执行所装饰的函数并返回其响应
            return f(*args,**kwargs)
    return wrap

