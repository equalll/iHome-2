# -*- coding:utf-8 -*-
import redis
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from config import config
from utils.common import RegexConverter
# 初始化redis
redis_store =None
# 初始化数据库连接
db = SQLAlchemy()
csrf=CSRFProtect()

# 初始化redis
redis_store = None
# 初始化数据库连接
db = SQLAlchemy()
# 开启CSRF保护
csrf = CSRFProtect()

# 设置日志的记录等级
logging.basicConfig(level=logging.DEBUG)  # 调试debug级
# 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024*1024*100, backupCount=10)
# 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
# 为刚创建的日志记录器设置日志记录格式
file_log_handler.setFormatter(formatter)
# 为全局的日志工具对象（flask app使用的）添加日志记录器
logging.getLogger().addHandler(file_log_handler)

def create_app(config_name):
    """工厂方法：工厂模式，通过工厂方法去根据传入的配置创建与该配置相关的app"""
    app =Flask(__name__)
    app.config.from_object(config[config_name])
    # 将当前app与db进行关联
    db.init_app(app)

    global redis_store
    redis_store=redis.StrictRedis(host=config[config_name].REDIS_HOST,port=config[config_name].REDIS_PORT)
    #print redis_store
    # 将当前app与csrf对象进行关联
    csrf.init_app(app)
    # # 给当前app的session设置保存路径
    Session(app)
    # 将自定义的正则转换器添加到转换器的字典中
    app.url_map.converters['re'] = RegexConverter
    # 注册api接口的蓝图
    from iHome.api_1_0 import api
    app.register_blueprint(api)

    # 注册静态文件的蓝图
    from web_html import html
    app.register_blueprint(html)

    return app



