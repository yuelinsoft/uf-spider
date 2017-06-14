# -*- coding:utf-8 -*-
"""
    __author__ = 'lijianbin'
    这个网站老变态了
"""


from __future__ import unicode_literals
import re
import json
from PIL import Image
from io import BytesIO
from EnterpriseCreditCrawler.common import image_recognition
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import RequestError

# 获取验证码图片
def get_cookies():
    """获取验证码图片Image对象，并返回cookies"""

    url = 'https://www.szcredit.org.cn/web/WebPages/Member/CheckCode.aspx'

    headers = {
        'Host': 'www.szcredit.org.cn',
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.87 Safari/537.36'),
        'Referer': 'https://www.szcredit.org.cn/web/GSPT/ShowCheckCode.aspx'
    }
    resp = url_requests.get(url, headers=headers, verify=False,
                            proxies=proxies)
    cookies = resp.cookies
    file = BytesIO(resp.content)
    image = Image.open(file)
    # image.show()
    return image, cookies

# 校验验证码
def verifyCode(checkCode, cookies):
    """

    :param checkCode: 识别后的验证码
    :return: 携带着的cookies
    """

    url = 'https://www.szcredit.org.cn/web/AJax/Ajax.ashx'
    headers = {
        'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
        'Host':'www.szcredit.org.cn',
        'Origin':'https://www.szcredit.org.cn',
        'Referer':'https://www.szcredit.org.cn/web/GSPT/ShowCheckCode.aspx',
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.87 Safari/537.36'),
        'X-Requested-With':'XMLHttpRequest'
    }
    data = {
        'action': 'GetCheckCode',
        'checkcode': checkCode
    }

    judge = url_requests.post(url, data=data, headers=headers,
                              cookies=cookies, proxies=proxies)

    judge = judge.text

    return judge

# 判断验证码是否识别正确
def recognize_code():
    """判断验证码是否识别正确

    正确就返回cookies，错误就返回None
    """

    image, cookies = get_cookies()
    # image.show()
    code = image_recognition.image_recognition(image, 'shenzhen')
    if not code:
        return None

    judge = verifyCode(checkCode=code, cookies=cookies)
    if '计算错误' in judge:
        return None

    return cookies

def get_results(company, cookies):
    """"""

    url = 'https://www.szcredit.org.cn/web/AJax/Ajax.ashx'

    headers = {
        'Host':'www.szcredit.org.cn',
        'Origin':'https://www.szcredit.org.cn',
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.87 Safari/537.36'),
        'X-Requested-With':'XMLHttpRequest'
    }

    data = {
        'action': 'GetEntList',
        'keyword': company,
        'type': 'load'
    }

    resp = url_requests.post(url=url,
                             data=data,
                             cookies=cookies,
                             headers=headers,
                             proxies=proxies)
    if '未查询到该企业的信息' in resp.text:
        print '未查询到该企业的信息，请重新输入！ '
        return []
    dic = json.loads(resp.text)
    msg = dic['msg'].split('（')[0]
    print msg
    resultList = dic['resultlist']
    results = []
    for each in resultList:
        item = {}
        # 获取企业名称
        patter = re.compile('<.*?>', re.S)
        item['company'] = re.sub(patter, '', each['EntName']).strip()
        # 组合链接
        detail = {}
        patter = re.compile('<.*?>', re.S)
        detail['company_name'] = re.sub(patter, '', each['EntName']).strip()
        detail['link'] = (
            'https://www.szcredit.org.cn/web/gspt/newGSPTDetail3.aspx?ID='+
            each['RecordID'])
        item['detail'] = detail
        results.append(item)
    return results


def main(**kwargs):
    name = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')
    # proxies = None  # 暂不使用动态IP
    # 限制验证码识别次数
    times = 1
    cookies = None
    while times < 20 and cookies == None:
        times += 1
        cookies = recognize_code()
    if cookies == None:
        raise RequestError('深圳验证码识别20次依然错误'.encode('utf-8'))

    results = get_results(company=name, cookies=cookies)

    return results




if __name__ == '__main__':
    name = ['深圳市兴业丰田汽车销售服务有限公司',
            '深圳市益群实业有限公司',
            '深圳市华星光电技术有限公司']
    main(name=name[2])
