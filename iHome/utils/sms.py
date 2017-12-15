# coding=utf-8

# -*- coding: UTF-8 -*-

from iHome.libs.yuntongxun.CCPRestSDK import REST
import ConfigParser

# 脰梅脮脢潞脜
accountSid = '8a216da86010e69001603110ee2a0e9f';

# 脰梅脮脢潞脜Token
accountToken = '413bb3e3591844919bbc19a6c4216a29';

# 脫娄脫脙Id
appId = '8a216da86010e69001603110ee8a0ea6';

# 脟毛脟贸碌脴脰路拢卢赂帽脢陆脠莽脧脗拢卢虏禄脨猫脪陋脨麓http://
serverIP = 'app.cloopen.com';

# 脟毛脟贸露脣驴脷
serverPort = '8883';

# REST掳忙卤戮潞脜
softVersion = '2013-12-26';


# 路垄脣脥脛拢掳氓露脤脨脜
# @param to 脢脰禄煤潞脜脗毛
# @param datas 脛脷脠脻脢媒戮脻 赂帽脢陆脦陋脢媒脳茅 脌媒脠莽拢潞{'12','34'}拢卢脠莽虏禄脨猫脤忙禄禄脟毛脤卯 ''
# @param $tempId 脛拢掳氓Id

class CCP(object):
    def __new__(cls, *args, **kwargs):
        if not hasattr(cls,"_instance"):
            cls._instance = super(CCP, cls).__new__(cls,*args,**kwargs)
            cls._instance.rest = REST(serverIP, serverPort, softVersion)
            cls._instance.rest.setAccount(accountSid, accountToken)
            cls._instance.rest.setAppId(appId)
        return cls._instance

    def send_template_sms(self,to, datas, tempId):
        # 鲁玫脢录禄炉REST SDK
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