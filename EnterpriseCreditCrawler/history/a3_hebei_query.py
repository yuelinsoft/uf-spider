# -*- coding:utf-8 -*-
"""
    __author__ = 'lijb'
    the same as 上海、云南（如果这里改动了，可能上海、云南的也需要更改。）
    该脚本实现的功能：
    1、访问河北省企业信用公示信息首页，获取cookie
    2、访问验证码弹窗地址，获取token
    3、访问验证码地址，获取验证码
    4、用1,2,3获取到的参数 + 查询的企业名称 返回企业信息的链接或者访问参数（params）

"""

from __future__ import unicode_literals
import re
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.image_recognition import image_recognition
from EnterpriseCreditCrawler.common.uf_exception import (StopException,
                                                         ReRunException)
from PIL import Image
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO, BytesIO

def get_cookies_token():
    """访问首页获取cookie"""

    url = 'http://www.hebscztxyxx.gov.cn/notice/home'
    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36'),
    }

    try:
        response = url_requests.get(url,
                                    headers=headers,
                                    timeout=10)
        session_token = re.search('"session.token": "(.*?)"', response.text,
                                  re.S).group(1)
        cookies = response.cookies

    except Exception as err:
        raise err

    return cookies, session_token

def get_checkCode(cookies):
    """用首页的cookie访问验证码，返回验证码字符串

    params:
        cookies: 访问首页时产生的cookies值
    """
    url = 'http://www.hebscztxyxx.gov.cn/notice/captcha?preset=0'
    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64)'
                       'AppleWebKit/537.36 (KHTML, like Gecko)'
                       'Chrome/54.0.2840.71 Safari/537.36'),
        # 'Referer': 'http://www.hebscztxyxx.gov.cn/notice/search/'
        #            'popup_captcha',
    }
    response = url_requests.get(url,
                                headers=headers,
                                cookies=cookies,
                                timeout=10)
    f = BytesIO(response.content)
    image = Image.open(f)
    image.show()
    checkCode = raw_input('please input the checkCode: ')
    # checkCode = image_recognition(image, 'hebei', config='-psm 10 digits')
    return checkCode

def verifyCode(checkCode, token):
    """检查验证码是否识别正确

    :param checkCode:
    :param token:
    :return:
    """

    url = 'http://www.hebscztxyxx.gov.cn/notice/security/verify_captcha'
    data = {
        'captcha': checkCode,
        'session.token': token
    }
    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36'),
        'Referer': 'http://www.hebscztxyxx.gov.cn/notice /'
    }

    response = url_requests.post(url, data=data, headers=headers)

    return response.text

def get_params(search_tag, checkCode, token, cookies):
    """获取可以访问data.py的参数或者链接

    :param search_tag: 所搜索的企业名称
    :param checkCode: 调用 get_checkCode 返回的验证码字符串
    :param token: 调用 get_token 返回的 session.token 参数
    :param cookies: 调用 get_cookies 返回的 cookies 值
    :return: 参数或者链接
    """

    url = 'http://www.hebscztxyxx.gov.cn/notice/search/ent_info_list'
    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36'),
        'Referer': 'http://www.hebscztxyxx.gov.cn/notice/home'
    }
    data = {
        'condition.pageNo': 1,
        'captcha': checkCode,
        'session.token': token,
        'condition.keyword': search_tag
    }
    try:
        response = url_requests.post(url,
                                     data=data,
                                     headers=headers,
                                     cookies=cookies,
                                     timeout=10)
    except Exception as err:
        raise err

    result_list = []
    soup = BeautifulSoup(response.text, 'lxml')
    links = soup.find_all('div', {'class': 'list-item'})
    if links == []:
        raise StopException("未查询到相关企业信息……")
    for each_link in links:
        link = each_link.find('a')['href']
        result_list.append(link)

    return result_list

times = 0   # 当验证码识别错误，重新识别的次数。

def main(**kwargs):
    """整体逻辑主函数

    :param kwargs:
    :return:
    """

    global times
    search_tag = kwargs.get('name')

    cookies, token = get_cookies_token()

    checkCode = get_checkCode(cookies=cookies)

    judge = verifyCode(checkCode, token)

    if judge == '1':
        params = get_params(search_tag, checkCode, token, cookies)

        return params
    else:

        print '验证码识别失败，程序将自动重新识别%s次……' % (10 - times)

        times += 1
        if times > 10:
            raise ReRunException('程序自动识别失败，请稍后重试。')

        return main(name=name)


if __name__ == '__main__':

    name = '邯郸市第二钢铁厂'

    print main(name=name)

    # http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=707iXuYXlgmvdVRSdLEvgmMm2x4nwYP9&tab=01 # 邢台钢铁制造厂(备案信息，【翻页】)
    # http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=u9Abs75MdJg1F0Fo03NLG_aqqjwgQhBN&tab=01 # 河北钢铁交易中心（变更信息）
    # http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=SImc_ZtmZNduaTU5NNKzqCAGXWDGM3aD&tab=01 # 邯郸市第二钢铁厂（经营异常）