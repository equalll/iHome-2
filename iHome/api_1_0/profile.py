# -*- coding:utf-8 -*-
from iHome import db
from iHome.utils.image_storage import storage_image
from iHome.utils.response_code import RET
from . import api
from flask import request,session,current_app, jsonify
from  iHome.models import User
from iHome.constants import QINIU_DOMIN_PREFIX
@api.route("/avatar",methods=["POST"])

def save_image():
    """
0. TODO 判断用户是否登录
1. 获取到上传的文件
2. 再将文件上传到七牛云
3. 将头像信息更新到当前用户的模型中
4. 返回上传的结果<avatar_url>
:return:
"""
    user_id =session.get("user_id")
    try:
        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")


    try:
        url = storage_image(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户数据错误")

    try:
        user = User.query.get("user_id")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    # 设置用户模型相关数据

    user.avatar_url = url
    try:
        db
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存用户数据错误")

    # 4. 返回上传的结果<avatar_url>
    return jsonify(errno=RET.OK, errmsg="OK",data={"avatar_url":QINIU_DOMIN_PREFIX+url})


