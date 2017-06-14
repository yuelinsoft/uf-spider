#coding=utf-8
import datetime
import time
current_milli_time = lambda: int(round(time.time() * 1000))
# 状态码的描述
_code_desc = {
    2000: u'流程成功,有数据',
    2100: u'支付宝登录失败',
    4000: u'点击我的支付宝失败',
    4100: u'手机文本框定位失败',
    4200: u'登录页面加载失败',
    4400: u'手机验证码错误',
    4444: u'点击"校验收款人姓名"按钮出错',
    4500: u'',
    4600: u'',
    4610: u'',
    4800: u'',
    5000: u'',
    5500: u''
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
        'time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
# end
