# -*- coding:utf-8 -*-
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config

# app=Flask(__name__)
# app.config.from_object(Config)

# #初始化数据库链接
# db = SQLAlchemy(app)
# # 初始化redis
# redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
# #kaiqi开启CSRF 保护
# csrf = CSRFProtect(app)
# # 给当前app的session设置保存路径
# Session(app)

# 初始化redis
redis_store =None
# 初始化数据库连接
db = SQLAlchemy()
csrf=CSRFProtect()

def create_app(config_name):
    """工厂方法：工厂模式，通过工厂方法去根据传入的配置创建与该配置相关的app"""
    app =Flask(__name__)
    app.config.from_object(config[config_name])
    # 将当前app与db进行关联
    db.init_app(app)

    global redis_store
    redis_store=redis.StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)
    print redis_store
    # 将当前app与csrf对象进行关联
    csrf.init_app(app)
    # # 给当前app的session设置保存路径
    Session(app)
    return app



