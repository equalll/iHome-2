# -*- coding:utf-8 -*-
from iHome import db
from iHome.utils.image_storage import storage_image
from iHome.utils.response_code import RET
from . import api
from flask import request,session,current_app, jsonify
from  iHome.models import User
from iHome.constants import QINIU_DOMIN_PREFIX
from flask import g
from iHome.utils.common import login_required

@api.route("/user/auth",methods=["POST"])
@login_required
def set_real():
    user_id=g.user_id
    real_data = request.json
    real_name = real_data.get("real_name")
    id_card = real_data.get("id_card")

    try:
        user=User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.USERERR,errmsg="用户不存在或未激活")
    user.real_name = real_name
    user.id_card = id_card

    if not user:
        return jsonify(errno=RET.USERERR,errmsg="用户不存在或未激活")

    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.DATAERR,errmsg="数据保存错误")

    return jsonify(errno=RET.OK,errmsg="ok")

@api.route("/user/auth")
@login_required
def get_real():
    user_id=g.user_id
    try:
        user=User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.USERERR,errmsg="用户不存在或未激活error")

    if not user:
        return jsonify(errno=RET.USERERR,errmsg="用户不存在或未激活",data=user.to_dict())

    real_name=user.real_name
    id_card=user.id_card

    to_dict={
        "real_name": real_name,
        "id_card": id_card
    }
    return jsonify(errno=RET.OK,errmsg="OK",data=to_dict)

@api.route("/users")
@login_required
def get_user_info():
    """
    获取用户信息
    1. 获取到当前登录的用户模型
    2. 返回模型中指定内容
    :return:
    """
    user_id =g.user_id
    try:
        user=User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    resp_dict ={
        "name":user.name,
        "avatar_url":QINIU_DOMIN_PREFIX+user.avatar_url,
        "mobile":user.mobile
    }
    return jsonify(errno=RET.OK, errmsg="OK", data=resp_dict)

@api.route("/user/avatar",methods=["POST"])
@login_required
def save_image():
    # user_id =session.get("user_id")
    user_id = g.user_id
    try:

        avatar_file = request.files.get("avatar").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    #     """
    # 0.  判断用户是否登录
    # 1. 获取到上传的文件
    # 2. 再将文件上传到七牛云
    # 3. 将头像信息更新到当前用户的模型中
    # 4. 返回上传的结果<avatar_url>
    # :return:
    # """

    try:
        url = storage_image(avatar_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="获取用户数据错误")


    try:
        user = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    # 设置用户模型相关数据
    if not user:
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")

    user.avatar_url = url
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存用户数据错误")

    # 4. 返回上传的结果<avatar_url>
    return jsonify(errno=RET.OK, errmsg="OK",data={"avatar_url":QINIU_DOMIN_PREFIX+url})

@api.route('/user/name',methods=["POST"])
@login_required
def save_user_name():
    """
     0. TODO 判断用户是否登录
     1. 获取到传入参数
     2. 将用户名信息更新到当前用户的模型中
     3. 返回结果
     :return:
     """
    data_dict = request.json
    name = data_dict.get("name")
    if not name:
        return jsonify(errno=RET.PARAMERR, errmsg="参数不完整")

    # user_id =session.get("user_id")
    user_id = g.user_id
    # try:
    #     user_name=request.json.get("name")
    # except Exception as e:
    #     current_app.logger.error(e)
    #     return jsonify()

    user=User.query.get(user_id)
    user.name=name
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=RET.USERERR, errmsg="用户不存在")
    session["name"]=name
    return  jsonify(errno=RET.OK, errmsg="OK")

