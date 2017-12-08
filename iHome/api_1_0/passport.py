# -*- coding:utf-8 -*-
from flask import current_app
# 实现注册和登录的逻辑

from flask import current_app
from . import api
from flask import request, jsonify
from iHome.utils.response_code import RET
from iHome import redis_store, db
from iHome.models import User


@api.route("/user", methods=["POST"])
def register():
    """
    1. 获取参数和判断是否有值
    2. 从redis中获取指定手机号对应的短信验证码的
    3. 校验验证码
    4. 初始化 user 模型，并设置数据并添加到数据库
    5. 保存当前用户的状态
    6. 返回注册的结果
    :return:
    """
    data_dict = request.json
    mobile = data_dict.get("mobile")
    phonecode = data_dict.get("phonecode")
    password = data_dict.get("password")

    if not all([mobile, phonecode, password]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

    # 2. 从redis中获取指定手机号对应的短信验证码的
    try:
        sms_code = redis_store.get("SMS_"+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取本地验证码失败")

    if not sms_code:
        return jsonify(errno=RET.NODATA, errmsg="短信验证码过期")

    # 3. 校验验证码
    if phonecode != sms_code:
        return jsonify(errno=RET.DATAERR, errmsg="短信验证码错误")

        # 4. 初始化 user 模型，并设置数据并添加到数据库
    user =User()
    user.name = mobile
    user.name = mobile
    # aODO: 对密码进行处理
    #  对密码进行处理
    user.password = password
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR, errmsg="数据保存错误")
    return jsonify(errno=RET.OK, errmsg="注册成功")
