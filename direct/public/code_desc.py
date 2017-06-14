#coding=utf-8
import datetime


# 状态码的描述
_code_desc = {
    2000: u'流程成功,有数据',
    2100: u'流程成功,无数据',
    4000: u'网络错误',
    4100: u'解析错误',
    4200: u'验证码无法识别',
    4400: u'参数错误',
    4444: u'简版征信身份验证码错误',
    4500: u'账号错误',
    4600: u'密码错误',
    4610: u'手机动态码错误',
    4800: u'查询失败',
    5000: u'对方服务器错误',
    5500: u'对方服务器繁忙'
}
_code_keys = _code_desc.keys()

def returnResult(code, data, desc=''):
    """ 统一格式化返回
    :param code: 状态码
    :param desc: 返回描述
    :param data: 数据/内容
    :return: dict(code=xx, desc=xx, data=xx, time=xx)
    """
    if code not in _code_keys and desc=='':
        raise ValueError(u'危险:未知状态码的描述不可缺省')
    else:
        desc = _code_desc[code] if desc == '' else desc
    return {
        'code': code,
        'desc': desc,
        'data': data,
        'time': datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    }
# end

