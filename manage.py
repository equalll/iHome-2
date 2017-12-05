# -*- coding:utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import redis
from flask_wtf.csrf import CSRFProtect

class Config():
    """配置信息类"""
    SECRET_KEY = "bxOaxOKPaeZaipSvq7rjfeYtYvG5jPvwIgGZsteuTGhTSrKAHh/Q6eGHQm2Yw671"
    DEBUG=True

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/ihome"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # redis 连接配置
    REDIS_HOST="127.0.0.1"
    REDIS_PORT = 6379

app=Flask(__name__)
app.config.from_object(Config)
#初始化数据库链接
db = SQLAlchemy(app)
# 初始化redis
redis_store = redis.StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
#kaiqi开启CSRF 保护
csrf = CSRFProtect(app)

@app.route("/",methods=["GET","POST"])
def index():
    redis_store.set('name','xiaoruirui')
    return "index"


if __name__ == '__main__':
    app.run()