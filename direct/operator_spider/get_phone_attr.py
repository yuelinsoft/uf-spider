#coding=utf-8
import json
from ..public import (
    Request,
    returnResult
)

def getPhoneAttr(phone_num):
    """ 调用百度api获得手机的归属地
    :param phone_num: 手机号
    :return:统一接口返回
    example:
        >>searchPhoneInfo('15802028888')
        正常返回key data对应的元素例子
        {'phone':'13267175437', 'province':'广东', 'city':'深圳', 'company':1}
        company值:中国联通1; 中国移动2; 中国电信3, 其他4
    """
    _company_convert = {
        u'中国联通': 1,
        u'中国移动': 2,
        u'中国电信': 3
    }
    phone_num = str(phone_num).strip()
    phone_status = 6855 if phone_num[0] == '0' else 6004
    url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
    params = {'query':phone_num, 'resource_id': phone_status}
    options = {'method': 'get', 'url': url, 'params': params}

    response = Request.basic(options)
    if response:
        try:
            company_type = 4
            item = json.loads(response.text)['data'][0]
            if item['type'] in _company_convert.keys():
                company_type =  _company_convert[item['type']]
            data = {
                'phone': phone_num,
                'province': item['prov'],
                'city': item['city'],
                'company': company_type
            }
            return returnResult(code=2000, data=data, desc=u'查询成功')
        except (KeyError, IndexError):
            return returnResult(code=4500, data={})
        except (ValueError, Exception):
            return returnResult(code=4100, data={})
    else:
        return returnResult(code=4000, data={})
# end




