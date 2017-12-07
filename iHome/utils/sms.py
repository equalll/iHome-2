# coding=gbk

# coding=utf-8

# -*- coding: UTF-8 -*-

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# Ö÷ÕÊºÅ
accountSid = '8aaf07085f5c54cf015f8c1710fa0f4d';

# Ö÷ÕÊºÅToken
accountToken = '711b641d76b34b06ab1a1fbc07fd381c';

# Ó¦ÓÃId
appId = '8aaf07085f5c54cf015f8c1712620f54';

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


            # sendTemplateSMS("18513174598", ["999999", "5"], "1")