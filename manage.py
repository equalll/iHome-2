# -*- coding:utf-8 -*-
from flask import session
from flask_script import Manager
from flask_migrate import Migrate,MigrateCommand
from iHome import db,create_app

app=create_app("development")
manager = Manager(app)
#集成数据库的迁移
Migrate(app,db)
manager.add_command('db',MigrateCommand)

@app.route("/",methods=["GET","POST"])
def index():
    session["name"] ="xiaohua"
    # redis_store.set('name','xiaoruirui')
    return "index yujjinneng222"


if __name__ == '__main__':
    manager.run()