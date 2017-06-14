#coding=utf-8
from ..public import returnResult
from get_phone_attr import getPhoneAttr
from china_unicom import chinaUnicomAPI



def phone_distribute(phone, password):
    # 根据号码进行分发[目前只支持中国联通]
    phone_attr = getPhoneAttr(phone)
    if phone_attr['code'] == 2000:
        phone_attr = phone_attr['data']
        if phone_attr['company'] == 1: # 联通
            phone_attr['password'] = password
            return get_unicom(phone_attr)
        else:
            return returnResult(
                code=4400,
                data={},
                desc=u'目前仅支持联通查询'
            )
    else:
        return returnResult(
            code=4800,
            data={},
            desc=u'查询手机属性外部接口失败'
        )


def get_unicom(phone_attr):
    # 中国联通
    return chinaUnicomAPI(phone_attr)


def get_china():
    # 中国移动
    return None


def get_telecom():
    # 中国电信
    return None









