# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# Ö÷ÕÊºÅ
accountSid = '8a216da86010e69001603110ee2a0e9f';

# Ö÷ÕÊºÅToken
accountToken = '413bb3e3591844919bbc19a6c4216a29';

# Ó¦ÓÃId
appId = '8a216da86010e69001603110ee8a0ea6';

# ÇëÇóµØÖ·£¬¸ñÊ½ÈçÏÂ£¬²»ÐèÒªÐ´http://
serverIP = 'app.cloopen.com';

# ÇëÇó¶Ë¿Ú
serverPort = '8883';

# REST°æ±¾ºÅ
softVersion = '2013-12-26';


# ·¢ËÍÄ£°å¶ÌÐÅ
# @param to ÊÖ»úºÅÂë
# @param datas ÄÚÈÝÊý¾Ý ¸ñÊ½ÎªÊý×é ÀýÈç£º{'12','34'}£¬Èç²»ÐèÌæ»»ÇëÌî ''
# @param $tempId Ä£°åId

def sendTemplateSMS(to, datas, tempId):
    # ³õÊ¼»¯REST SDK
    rest = REST(serverIP, serverPort, softVersion)
    rest.setAccount(accountSid, accountToken)
    rest.setAppId(appId)

    result = rest.sendTemplateSMS(to, datas, tempId)
    for k, v in result.iteritems():

        if k == 'templateSMS':
            for k, s in v.iteritems():
                print '%s:%s' % (k, s)
        else:
            print '%s:%s' % (k, v)


# sendTemplateSMS("17695738212", ["999999", "5"], "1")