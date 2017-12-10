# -*- coding:utf8 -*-
from flask import current_app, jsonify

from iHome import redis_store
from iHome.constants import AREA_INFO_REDIS_EXPIRES
from iHome.utils.response_code import RET
from . import api
from iHome.models import Area
@api.route("/areas")
def get_areas():
    """
    1. 查询出所有的城区
    2. 返回
    :return:
    """

    # 先从redis中查询
    try:
        areas_dict = redis_store.get("areas")
    except Exception as e:
        current_app.logger.error(e)

    if areas_dict:
        return jsonify(errno=RET.OK, errmsg="ok",data=eval(areas_dict))

    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="数据库查询错误")

     # 因为不能直接返回对象数组，所以定义一个列表，去中保存每一个模型所对应的字典信息
    areas_dict=[]
    for area in areas:
        areas_dict.append(area.to_dict())
        # print area.to_dict

    # 将数据保存到redis中
    try:
        redis_store.set("areas",areas_dict,AREA_INFO_REDIS_EXPIRES)
    except Exception  as e:
        current_app.logger.error(e)
    return jsonify(errno=RET.OK,errmsg="OK",data=areas_dict)

