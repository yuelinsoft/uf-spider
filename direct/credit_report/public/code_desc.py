#coding=utf-8
import time
now = time.strftime("%Y-%m-%d  %H:%M:%S")

#状态码的描述
exception_code={
    100:u'重新爬取',
    101:u'停止爬取'
}

_code_desc={
    2000:u'流程成功',
    4000:u'网络错误',
    4100:u'解析错误',
    4200:u'验证码无法识别',
    4400:u'参数错误',
    4444:u'简版征信身份证码错误',
    4500:u'账号错误',
    4600:u'密码错误',
    4610:u'手机动态码错误',
    4800:u'查询失败',
    5000:u'对方服务器错误',
    5500:u'对方服务器繁忙'
}
_code_keys=_code_desc.keys()
def returnResult(code,data,desc=""):
    """统一格式返回
    :param code:状态码
    :param data:数据内容
    :param desc:返回描述
    :return:
    """
    if code not in _code_keys and desc=="":
        raise ValueError(u'危险：未知状态码的描述不可缺省')
    else:
        desc=_code_desc[code] if desc=='' else desc

#最终返回一个字典
    return dict(code=code,desc=desc,
                data=data,time=now)
