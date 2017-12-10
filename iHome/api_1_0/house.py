# -*- coding:utf8 -*-
from flask import current_app, jsonify
from iHome.utils.response_code import RET
from . import api
from iHome.models import Area
@api.route("/areas")
def areas():
    try:
        areas = Area.query.all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DATAERR,errmsg="数据库查询错误")

     # 因为不能直接返回对象数组，所以定义一个列表，去中保存每一个模型所对应的字典信息
    area_dict=[]
    for area in areas:
        area_dict.append(area.to_dict())
        # print area.to_dict
    return jsonify(errno=RET.OK,errmsg="OK",data=area_dict)

