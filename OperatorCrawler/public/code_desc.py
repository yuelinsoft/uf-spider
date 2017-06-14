#coding=utf-8
import datetime

# 状态码的描述
_code_desc = {
    2000: u'流程成功,有数据',
    2001: u'流程成功,部分有数据',
    2100: u'流程成功,无数据',
    4000: u'网络错误',
    4100: u'解析错误',
    4200: u'验证码无法识别',
    4400: u'参数错误',
    4444: u'简版征信身份验证码错误',
    4500: u'账号错误',
    4600: u'用户名或密码错误',
    4610: u'手机动态码错误',
    4800: u'查询失败',
    5000: u'对方服务器错误',
    5500: u'对方服务器繁忙',
    7001: u'运营商服务器繁忙，弹出了验证码',
    7002: u'密码过于简单，不支持登录',
    7005: u'您的号码所属省份系统正在升级，请稍后再试'
}

_code_keys = _code_desc.keys()

def return_result(code, data, desc='', **kwargs):
    # 尽量不要让desc为空，最好是提前捕获到exception。
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
    if 'func' in kwargs:
        desc = kwargs['func'] + ': ' + desc
    # print {
    #     'code': code,
    #     'desc': desc,
    #     'data': data,
    #     'time': datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    #     }
    return {
        'code': code,
        'desc': desc,
        'data': data,
        'time': datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    }
# end

def test_rr():
    a = dict(
        code=4000,
        # func='sys_check_login',
        desc = 'well done'
    )
    return return_result(
        code=a['code'],
        data=a['data'] if a.has_key('data') else {},
        desc=a['desc'] if a.has_key('desc') else '',
        func=a['func'] if a.has_key('func') else ''
    )


if __name__ == "__main__":
    print test_rr()
