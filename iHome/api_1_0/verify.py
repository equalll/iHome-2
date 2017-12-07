# -*- coding:utf-8 -*-
from iHome.utils.response_code import RET
from flask import request,abort,current_app,jsonify,make_response
from . import api
from iHome import redis_store
from iHome import constants
from iHome.utils.captcha.captcha import captcha

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
