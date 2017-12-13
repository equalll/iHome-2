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

@api.route("/orders/comment",methods=["PUT"])
@login_required
def order_comment():
    """
    订单评价
    1. 获取参数
    2. 校验参数
    3. 修改模型
    :return:
    """

    # 1. 获取参数
    data_json = request.json
    order_id = data_json.get("order_id")
    comment = data_json.get("comment")

    # 2. 2. 校验参数
    if not all([order_id,comment]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        order = Order.query.filter(Order.id == order_id,Order.status =="WAIT_COMMENT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据错误")

    if not order:
        return jsonify(errno=RET.NODATA, errmsg="该订单不存在")
        # 3. 修改模型并且保存到数据库
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    # 4 返回结果
    return jsonify(errno=RET.OK, errmsg="ok")

@api.route('/orders',methods=["PUT"])
@login_required
def change_order_status():
    """
    1. 接受参数：order_id
    2. 通过order_id找到指定的订单，(条件：status="待接单")
    3. 修改订单状态
    4. 保存到数据库
    5. 返回
    :return:
    """
    user_id = g.user_id
    data_json = request.json
    # 取到订单号
    order_id = data_json.get("order_id")
    action = data_json.get("action")

    if not order_id:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if action not in ("accept","reject"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 2. 查询订单
    try:
        order = Order.query.filter(Order.id == order_id,Order.status=="WAIT_ACCEPT").first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not order:
        return jsonify(errno=RET.NODATA, errmsg="未查询到订单")

        # 查询当前订单的房东是否是当前登录用户，如果不是，不允许操作
    if user_id != order.house.user_id:
        return jsonify(errno=RET.ROLEERR, errmsg="不允许操作")

        # 3 更改订单的状态
    if action == "accept":
        order.status = "WAIT_COMMENT"
    elif action == "reject":
        order.status = "REJECTED"
        reason = data_json.get("reason")
        # 取出原因
        if not reason:
            return jsonify(errno=RET.PARAMERR,errmsg="请填写拒单原因")
        # 保存拒单原因
        order.comment = reason

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")

    return jsonify(errno=RET.OK,errmsg="OK")
@api.route("/orders")
@login_required
def get_orders():
    """
    1. 去订单的表中查询当前登录用户下的订单
    2. 返回数据
    :return:
    """
    user_id = g.user_id
    # 取当前角色的标识：房客：custom,房东：landlord
    role = request.args.get("role")

    if not role:
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    if role not in("custom","landlord"):
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    try:
        if role=="custom":# 房客订单查询
            orders = Order.query.filter(Order.user_id==user_id).order_by(Order.create_time.desc()).all()
        elif role=="landlord": # 房东订单查询
            # 1. 先查出当前登录用户的所有的房屋, House
            houses = House.query.filter(House.user_id==user_id).all()
            house_ids=[house.id for house in houses]
            # 2. 取到所有的房屋id
            # 3. 从订单表中查询出房屋id在第2步取出来的列表中的房屋
            orders = Order.query.filter(Order.house_id.in_(house_ids)).order_by(Order.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    orders_dict_li =[]
    for order in orders:
        orders_dict_li.append(order.to_dict())
    return jsonify(errno=RET.OK, errmsg="OK", data={"orders": orders_dict_li})

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