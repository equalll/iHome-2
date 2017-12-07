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

class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,"_instance"):
            cls._instance = super(CCP, cls).__new__(cls,*args,**kwargs)
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
        return cls._instance

    def send_template_sms(self,to, datas, tempId):
        # ³õÊ¼»¯REST SDK
        result = self.rest.sendTemplateSMS(to, datas, tempId)
        if result.get("statusCode") == "000000":
            return 1
        else:
            return 0
        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print '%s:%s' % (k, s)
        #     else:
        #         print '%s:%s' % (k, v)
        #
if __name__ == '__main__':
    CCP().send_template_sms("17695738212", ["999999", "5"], "1")


# sendTemplateSMS("17695738212", ["999999", "5"], "1")