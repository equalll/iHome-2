# -*- coding:utf-8 -*-
import random
import re

from flask import json

from iHome.utils.response_code import RET
from flask import request,abort,current_app,jsonify,make_response

from iHome.utils.sms import CCP
from . import api
from iHome import redis_store
from iHome import constants
from iHome.utils.captcha.captcha import captcha

@api.route('/smscode',methods=["POST"])
def send_sms():
   """1 接收参数, 判断是否有值
    2 校验手机号是否合理
    3 取出传过来的图片ID, 去Redis查询对应的数值, 是否相等
    4 校验图片验证码是否正确
    5 生成内容, 给手机发送验证码
    6 保存手机验证码的内容和手机号ID
    7 返回发送成功的响应"""
   data=request.data
   data_dict = json.loads(data)
   mobile = data_dict.get("mobile")
   image_code = data_dict.get("imagecode")
   image_code_id = data_dict.get("imagecode_id")

   if not all([mobile,image_code,image_code_id]):
       return jsonify(errno=RET.PARAMERR, errmsg="参数不全")

   if not re.match("^1[3578][0-9]{9}$",mobile):
       return jsonify(errno=RET.PARAMERR, errmsg="手机号格式不正确")

   try:
       real_image_code = redis_store.get("ImageCode_"+image_code_id)
       if real_image_code:
           redis_store.delete("ImageCode_"+image_code_id)
   except Exception as e:
       current_app.logger.error(e)
       return jsonify(rerrno=RET.DBERR, errmsg="获取图片验证码失败")
   if image_code.lower() != real_image_code:
       return jsonify(errno=RET.DATAERR, errmsg="验证码输入错误")

    # 5生成内容, 给手机发送验证码
   phone_code = random.randint(0,999999)
   sms_code ="%06d"%phone_code
   # current_app.logger.info(sms_code)
   current_app.logger.debug("短信验证码的内容：%s" % sms_code)
   result = CCP().send_template_sms(mobile,[sms_code,constants.SMS_CODE_REDIS_EXPIRES / 60],"1")
   if result != 1:
       return jsonify(error=RET.THIRDERR,errmsg="发送短信失败")
       # 6. redis中保存短信验证码内容
   try:
       redis_store.set("SMS_"+mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
   except Exception as e:
       current_app.logger.error(e)
       return jsonify(errno=RET.DBERR, errmsg="保存短信验证码失败")
   # 7. 返回发送成功的响应
   return jsonify(errno=RET.OK, errmsg="发送成功")


@api.route("/imagecode")
def get_imae_code():
    """
     1. 获取传入的验证码编号，并编号是否有值
     2. 生成图片验证码
     3. 保存编号和其对应的图片验证码内容到redis
     4. 返回验证码图片
     :return:
     """
    # current_app.logger.error("error log")
    # 1. 获取传入的验证码编号，并编号是否有值
    args = request.args
    cur = args.get("cur")
    pre = args.get("pre")
    if not cur:
        abort(403)

    # 2. 生成图片验证码
    _,text,image=captcha.generate_captcha()
    current_app.logger.debug(text)
    # 删除之前保存的数据
    # 3. 保存编号和其对应的图片验证码内容到redis
    try:
        redis_store.delete("ImageCode_"+pre)
        redis_store.set("ImageCode_"+cur,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        # 保存出现错误，返回JSON数据提示错误
        return jsonify(errno=RET.DBERR, errmsg="保存验证码失败")
    # 4. 返回验证码图片

    reponse = make_response(image)
    return reponse
