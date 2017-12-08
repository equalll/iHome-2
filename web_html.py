# -*- coding:utf-8 -*-
# 提供静态的html访问的功能，可直接在根路由后面添加上文件名
from flask import Blueprint,current_app,make_response
from flask_wtf.csrf import generate_csrf
# 创建提供静态文件文件的蓝图
html = Blueprint("html",__name__)

# @html.route("/<file_name>")
# def get_html_file(file_name):
#     file_name = "html/"+file_name
#     return current_app.send_static_file(file_name)

@html.route('/<re(".*"):file_name>')
def get_html_file(file_name):
    # 如果用户输入的是根路由
    if not file_name:
        file_name="index.html"
    # 判断是否是网站的Logo，如果不是，添加前缀
    # 127.0.0.1/index
    # 127.0.0.1/favicon.ico
    # if file_name != "favicon.ico":
    if file_name != "favicon.ico":
        file_name ="html/"+file_name
    # return current_app.send_static_file(file_name)
    response = make_response(current_app.send_static_file(file_name))

    #生成csrf_token
    csrf_token = generate_csrf()
    #设置csrf_token
    response.set_cookie("csrf_token",csrf_token)
    return response
