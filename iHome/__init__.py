# -*- coding:utf-8 -*-
import redis
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from flask_session import Session
from  config import Config

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

