# -*- coding:utf-8 -*-
from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect
from flask_session import Session

class Config():
    """配置信息类"""
    # SECRET_KEY = "bxOaxOKPaeZaipSvq7rjfeYtYvG5jPvwIgGZsteuTGhTSrKAHh/Q6eGHQm2Yw671"
    DEBUG=True

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

app=Flask(__name__)
app.config.from_object(Config)
#初始化数据库链接
db = SQLAlchemy(app)
# 初始化redis
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
#kaiqi开启CSRF 保护
csrf = CSRFProtect(app)
# 给当前app的session设置保存路径
Session(app)

@app.route("/",methods=["GET","POST"])
def index():
    session["name"] ="xiaohua"
    redis_store.set('name','xiaoruirui')
    return "index"


if __name__ == '__main__':
    app.run()