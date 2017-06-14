# -*- coding:utf-8 -*-
"""
    __author__ = 'lijianbin'
    与河北省、云南省一样，如果这里更改了，那么河北省、云南省的也可能需要更改。
"""

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.image_recognition import image_recognition
from EnterpriseCreditCrawler.common.uf_exception import (StopException,
                                                         ReRunException)
from PIL import Image, ImageFile
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO, BytesIO
# import requests
# import warnings
import re

ImageFile.LOAD_TRUNCATED_IMAGES = True
# warnings.filterwarnings('ignore')
# warnings.simplefilter("ignore", UserWarning)
# requests.packages.urllib3.disable_warnings()


def get_cookies_token():
    """访问首页获取cookie"""

    url = 'https://www.sgs.gov.cn/notice/home'
    headers = {
        'Host': 'www.sgs.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36'),
    }
    try:
        response = url_requests.get(url,
                                    headers=headers,
                                    verify=False,
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
    url = 'https://www.sgs.gov.cn/notice/captcha?preset=0'
    headers = {
        'Host': 'www.sgs.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36')
    }
    response = url_requests.get(url,
                                headers=headers,
                                cookies=cookies,
                                verify=False,
                                timeout=10)
    f = BytesIO(response.content)
    image = Image.open(f)
    # image.show()
    # checkCode = raw_input('please input the checkCode: ')
    checkCode = image_recognition(image, 'shanghai', config='-psm 10 digits')
    # print checkCode
    return checkCode

def verifyCode(checkCode, token):
    """检查验证码是否识别正确

    :param checkCode:
    :param token:
    :return:
    """

    url = 'http://gsxt.ynaic.gov.cn/notice/security/verify_captcha'
    data = {
        'captcha': checkCode,
        'session.token': token
    }
    headers = {
        'Host': 'gsxt.ynaic.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36'),
        'Referer': 'http://gsxt.ynaic.gov.cn/notice /'
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

    url = 'https://www.sgs.gov.cn/notice/search/ent_info_list'
    headers = {
        'Host': 'www.sgs.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36'),
        'Referer': 'https://www.sgs.gov.cn/notice/home '
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
                                     verify=False,
                                     timeout=10)
    except Exception as e:
        raise e

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
        times += 1
        print '验证码识别失败，程序将自动重新识别%s次……' % (11 - times)
        if times > 100:
            raise ReRunException('程序自动识别失败，请稍后重试。')

        return main(name=name)


if __name__ == '__main__':
    name = '上海实业交通电器有限公司'
    print main(name=name)
