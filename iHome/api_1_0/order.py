# -*- coding:utf-8 -*-
import datetime

from flask import current_app
from flask import g, jsonify
from flask import request

from iHome import db
from iHome.models import House, Order
from iHome.utils.response_code import RET
from . import api
from iHome.utils.common import login_required

@api.route("/orders",methods=["POST"])
@login_required
def add_order():
    """
    1. 获取参数 > house_id, start_date_str, end_date_str
    2. 判断和校验参数
    3. 查询指定房屋id是否存在
    4. 判断当前时间段内该房屋是否有订单
    5. 生成订单模型，设置数据
    6. 数据保存
    7. 返回
    :return:
    """
    #1. 获取参数 > house_id, start_date_str, end_date_str
    user_id = g.user_id
    data_json = request.json
    house_id =data_json.get("house_id")
    start_date_str = data_json.get("start_date")
    end_date_str = data_json.get("end_date")

    #2
    if not all([house_id,start_date_str,end_date_str]):
        return jsonify(errno=RET.PARAMERR,errmsg="参数错误")

    try:
        # 将日期字符串转成 datetime 对象
        start_date = datetime.datetime.strptime(start_date_str,"%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        #判断开始时间与结束时间的大小 断言
        assert start_date<end_date ,Exception("结束时间必须大于开始时间")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    # 3. 判断房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not house:
        return jsonify(errno=RET.NODATA,errmsg="房屋不存在")

    if user_id == house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="房东不能预订")

    # 4. 判断该房屋指定时间段内是否有冲突的订单
    try:
        filters = [Order.house_id==house_id,Order.end_date>start_date,Order.begin_date<end_date]
        # 取到冲突订单的数量
        order_count = Order.query.filter(*filters).count()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    # 如果冲突订单的数量大于0，代表该房屋已被预订
    if order_count>0:
        return jsonify(errno=RET.DATAERR,errmsg="房屋已被预订")

        # 5. 生成订单模型
    order = Order()
    days = (end_date-start_date).days   #   duixiang时间对象
    order.user_id = user_id
    order.house_id = house_id
    order.begin_date = start_date
    order.end_date = end_date
    order.days = days
    order.house_price=house.price
    order.amount = days * house.price

    # 将房屋的订单数量加1
    house.order_count += 1

    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno = RET.OK,errmsg="OK")