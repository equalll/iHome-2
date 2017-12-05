# -*- coding:utf-8 -*-
from flask import Flask
app=Flask(__name__)

from flask_sqlalchemy import SQLAlchemy

app.route('/')
def index():
    return 'index'

class Config():
    DEBUG=True
    db = SQLAlchemy(app)


if __name__ == '__main__':
    app.run()