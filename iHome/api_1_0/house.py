# -*- coding:utf8 -*-
import datetime
from flask import current_app, jsonify
from flask import g
from flask import request
from flask import session

from iHome import constants
from iHome import redis_store, db
from iHome.constants import AREA_INFO_REDIS_EXPIRES, QINIU_DOMIN_PREFIX,HOUSE_DETAIL_REDIS_EXPIRE_SECOND, \
    HOME_PAGE_MAX_HOUSES, HOME_PAGE_DATA_REDIS_EXPIRES, HOUSE_LIST_PAGE_CAPACITY
from iHome.utils.common import login_required
from iHome.utils.image_storage import storage_image
from iHome.utils.response_code import RET
from . import api
from iHome.models import Area, House, HouseImage,Facility, Order


@api.route("/houses")
def get_house_list():
    """
    1. 先加载所有的房屋信息
    :return:
    """
    # 去查询所有数据
    args = request.args
    # 获取到前端需要查询的页数
    p = args.get("p","1")
    sk = args.get("sk","new")
    aid = args.get("aid","")
    start_date_str = args.get("start-date")   #"2017-12-12"
    end_date_str = args.get("end_date")
    # 2. 判断参数
    start_date=None
    end_date=None
    try:
        if start_date_str:
            start_date = datetime.datetime.strptime(start_date_str,"%Y-%m-%d")
        if end_date_str:
            end_date = datetime.datetime.strptime(end_date_str, "%Y-%m-%d")
        if start_date_str and end_date_str:
            assert start_date < end_date, Exception("end_date_str>start_date_str")
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")
    try:
        p=int(p)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数错误")

    # 先从缓存中去取数据
    try:
        redis_key = "house_list_%s_%s_%s_%s"%(start_date_str,end_date_str,aid,sk)
        response_dict = redis_store.hget(redis_key,p)
        if response_dict:
            return jsonify(errno=RET.OK, errmsg="OK", data=eval(response_dict))
    except Exception as e:
        current_app.logger.error(e)

    try:
        # houses = House.query.all()
        houses_query=House.query
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR,errmsg="查询数据失败")
    filters=[]
    if aid:
        filters.append(House.area_id == aid)

    # 添加日期过滤的条件：
    confilect_orders=None
    if start_date and end_date:
        confilect_orders = Order.query.filter(Order.begin_date < end_date,Order.end_date>start_date).all()
    elif start_date:
        confilect_orders = Order.query.filter(Order.end_date > start_date).all()
    elif end_date:
        confilect_orders = Order.query.filter(Order.begin_date < end_date).all()

    if confilect_orders:
        # 如果冲突的订单里面有值, 取到所有冲突订单的房屋id
        confilect_house_ids = [order.house_id for order in confilect_orders]
    # 给房屋的过滤列表添加条件：不包含冲突的房屋id的房屋
        filters.append(House.id.notin_(confilect_house_ids))

    # 添加排序逻辑
    if sk == "booking":
        houses_query = houses_query.filter(*filters).order_by(House.order_count.desc())
    elif sk == "price-inc":
        houses_query = houses_query.filter(*filters).order_by(House.price)
    elif sk == "price-des":
        houses_query = houses_query.filter(*filters).order_by(House.price.desc())
    else:
        houses_query = houses_query.filter(*filters).order_by(House.create_time.desc())
    # 进行分页 > 参1：查询第几页，参数2：每一页多少条，参数3：是否抛出错误
    paginate = houses_query.paginate(p,HOUSE_LIST_PAGE_CAPACITY,False)
    # 取到总页数
    total_page = paginate.pages
    # 取到当前页的数据
    houses = paginate.items
    house_dict = []
    for house in houses:
        house_dict.append(house.to_basic_dict())
    #缓存数据
    response_dict = {"houses":house_dict,"total_page":total_page}

    # 缓存数据
    try:
        redis_key =  "house_list_%s_%s_%s_%s" % (start_date_str, end_date_str, aid, sk)
    # 生成redis中的管道对象
        pipeline = redis_store.pipeline()
        # start     shiwu         # 开启事务
        pipeline.multi()
    # 保存数据 hash
        pipeline.hset(redis_key,p,response_dict)
    # 设置生命周期
        pipeline.expire(redis_key,constants.HOUSE_LIST_REDIS_EXPIRES)
    # 提交事务
        pipeline.execute()
    except Exception as e:
        current_app.logger.error(e)
    return jsonify(errno=RET.OK,errmsg="OK",data=response_dict)

@api.route("/houses/index")
def get_house_index():
    """
    1. 查询数据库 > order_by，limit
    2. 返回

    :return: 首页订单量最高的5条数据
    """
    # 先从缓存中去加载数据
    try:
        houses_dict = redis_store.get("home_house")
        if houses_dict:
            return jsonify(errno=RET.OK, errmsg="OK", data={"houses": eval(houses_dict)})
    except Exception as e:
        current_app.logger.error(e)

    try:
        houses = House.query.order_by(House.order_count.desc()).limit(HOME_PAGE_MAX_HOUSES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询数据失败")

    # 将对象列表转成字典列表
    houses_dict = []
    for house in houses:
        houses_dict.append(house.to_basic_dict())

    # 将数据进行缓存
    try:
        redis_store.set("home_house",houses_dict, HOME_PAGE_DATA_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)

    return jsonify(errno=RET.OK, errmsg="OK", data={"houses": houses_dict})

@api.route("/houses/<int:house_id>")
def get_house_detail(house_id):
    """
    1. 通过房屋的id查询出指定的房屋
    2. 将房屋的相关数据进行返回(房屋信息，当前登录用户的id)
    3. 考虑是否缓存的问题
    :param house_id:
    :return:
    """
    # 先尝试从redis中去取
    # 获取到当前登录用户的id，如果没有登录，那么就返回-1
    user_id = session.get("user_id",-1)
    try:
        house_dict = redis_store.get(("house_detail_%d" %house_id))
        if house_dict:
            # 如果取到有数据，那么直接返回
            return jsonify(errno=RET.OK, errmsg="OK", data={"user_id": user_id, "house": eval(house_dict)})
    except Exception as e:
        current_app.logger.error(e)

    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据查询错误")

    if not house:
        return  jsonify(errno=RET.NODATA, errmsg="房屋不存在")

    house_dict=house.to_full_dict()
    # 缓存当前房屋数据
    try:
        redis_store.set(("house_detail_%d"%house_id),house_dict,HOUSE_DETAIL_REDIS_EXPIRE_SECOND )
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.OK, errmsg="OK", data={"user_id": user_id, "house": house_dict})

@api.route("/houses/<int:house_id>/images",methods=["POST"])
@login_required
def upload_house_image(house_id):
    """
    1. 取到上传的图片
    2. 进行七牛云上传
    3. 将上传返回的图片地址存储
    4. 进行返回
    :return:
    """

    # 1. 取到上传的图片
    try:
        house_image_file = request.files.get("house_image").read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数不全")


    # 2. 查询房屋是否存在
    try:
        house = House.query.get(house_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="查询房屋失败")

    if not house:
        return jsonify(errno=RET.NODATA, errmsg="房屋不存在")
    # 3. 上传到七牛云
    try:
        url = storage_image(house_image_file)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.THIRDERR,errmsg="上传图片失败")

        # 4. 初始化房屋的图片模型
    house_image = HouseImage()
    house_image.house_id = house.id
    house_image.url = url

    # 判断是否有首页图片
    if not house.index_image_url:
        house.index_image_url=url

    # 更新到数据库
    try:
        db.session.add(house_image)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="保存数据失败")
    return jsonify(errno=RET.OK,errmsg="OK",data={"url":QINIU_DOMIN_PREFIX +url})

@api.route("/houses",methods=["POST"])
@login_required
def save_new_house():
    """
    1. 接收参数并且判空
    2. 将参数的数据保存到新创建house模型
    3. 保存house模型到数据库
    前端发送过来的json数据
    {
        "title":"",
        "price":"",
        "area_id":"1",
        "address":"",
        "room_count":"",
        "acreage":"",
        "unit":"",
        "capacity":"",
        "beds":"",
        "deposit":"",
        "min_days":"",
        "max_days":"",
        "facility":["7","8"]
    }
    :return:
    """

    # 1. 取到参数

    user_id = g.user_id

    json_dict = request.json
    title = json_dict.get('title')
    price = json_dict.get('price')
    address = json_dict.get('address')
    area_id = json_dict.get('area_id')
    room_count = json_dict.get('room_count')
    acreage = json_dict.get('acreage')
    unit = json_dict.get('unit')
    capacity = json_dict.get('capacity')
    beds = json_dict.get('beds')
    deposit = json_dict.get('deposit')
    min_days = json_dict.get('min_days')
    max_days = json_dict.get('max_days')

    # 1.1 判断是否都有值
    if not all(
            [title, price, address, area_id, room_count, acreage, unit, capacity, beds, deposit, min_days, max_days]):
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    # 1.2 校验参数格式是否正确
    try:
        price = int(float(price) * 100)
        deposit = int(float(deposit) * 100)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=RET.PARAMERR, errmsg="参数有误")

    house = House()
    house.user_id = user_id
    house.area_id = area_id
    house.title = title
    house.price = price
    house.address = address
    house.room_count = room_count
    house.acreage = acreage
    house.unit = unit
    house.capacity = capacity
    house.beds = beds
    house.deposit = deposit
    house.min_days = min_days
    house.max_days = max_days

    # 获取到当前房屋的设施列表数组
    facilities = json_dict.get("facility")
    if facilities:
        house.facilities = Facility.query.filter(Facility.id.in_(facilities)).all()

    # 3.保存house模型到数据库
    try:
        db.session.add(house)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=RET.DBERR, errmsg="数据保存错误")

    return jsonify(errno=RET.OK, errmsg="ok", data={"house_id": house.id})

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

