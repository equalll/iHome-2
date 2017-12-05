# -*- coding:utf-8 -*-
import redis
class Config(object):
    """配置信息类"""
    SECRET_KEY = "bxOaxOKPaeZaipSvq7rjfeYtYvG5jPvwIgGZsteuTGhTSrKAHh/Q6eGHQm2Yw671"
    DEBUG = True
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis 连接配置
    REDIS_HOST="127.0.0.1"
    REDIS_PORT = 6379

    # session 的配置
    SESSION_TYPE ="redis"
    # 设置保存到的redis，默认如果没设置话，Flask-Session会帮我们创建一个redis
    SESSION_REDIS=redis.StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    SESSION_USE_SINGER =True
    PERMANENT_SESSION_LIFETIME = 86400

class DevelopmentConfig(Config):
    """开发环境下的配置"""
    DEBUG = True

class ProductionConfig(Config):
    """生产环境下的配置"""
    pass