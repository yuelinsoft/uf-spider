# -*- coding:utf-8 -*-
"""
    四川query

    @author： lijianbin
"""


from __future__ import unicode_literals
import os
import time
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common import captcha


def get_cookie():
    """访问首页获取cookies值"""

    url = 'http://gsxt.scaic.gov.cn/ztxy.do'

    headers = {
        'Host':'gsxt.scaic.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/52.0.2743.82 Safari/537.36')
    }

    random = str(int(time.time() * 1000))  # 13位的时间戳

    params = {'method': 'index', 'random': random}

    response = url_requests.get(url, params=params, headers=headers)

    cookies = response.cookies

    return cookies

def get_image(cookies):
    """获取验证码图片"""

    url = 'http://gsxt.scaic.gov.cn/ztxy.do'

    headers = {
        'Host': 'gsxt.scaic.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/52.0.2743.82 Safari/537.36')
    }

    random = str(int(time.time() * 1000))

    params = {
        'method':'createYzm',
        'dt':random,
        'random':random
    }

    response = url_requests.get(url, headers=headers, params=params)

    file = BytesIO(response.content)
    img = Image.open(file)

    return img

def cut_threeImg(Image):
    """将验证码切成出三个关键图

    :param Image: 二值image对象
    :return: three images
    """

    one = Image.crop((0,0,16,30))
    two = Image.crop((16,0,33,30))
    three = Image.crop((33,0,48,30))

    return one, two, three

def get_check(Image):
    """识别验证码，返回结果（jg）

    """

    path_a = os.path.dirname(__file__)
    path_a = os.path.abspath(os.path.join(path_a, '..'))
    abs_path = os.path.join(path_a,
                            'train_operator/f2_sichuan_train_operator.csv')
    trains, labels = captcha.loadTrainSet(abs_path)

    # 二值化
    img = captcha.twoValueImage(Image, 120)

    # 切出三个来
    imgs = cut_threeImg(img)
    images = []
    for each in imgs:
        each = captcha.cutAround(each)
        each = captcha.formatImg(each, (20, 20))
        images.append(each)

    # 识别出三个来
    one = captcha.classify_SVM(images[0], trains, labels)
    two = captcha.classify_SVM(images[1], trains, labels)
    three = captcha.classify_SVM(images[2], trains, labels)
    if two == '+':
        jg = int(one) + int(three)
    else:
        jg = int(one) * int(three)

    return jg

def get_query(name, checkCode, cookies):
    """获取查询结果

    :param name: 公司名
    :param checkCode: 验证码
    :param cookies: cookie
    :return: 搜索结果的url的id参数列表  type：list
    """

    htmlId = []

    url = 'http://gsxt.scaic.gov.cn/ztxy.do'

    headers = {
        'Host':'gsxt.scaic.gov.cn',
        'Origin':'http://gsxt.scaic.gov.cn',
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/52.0.2743.82 Safari/537.36')
    }

    random = str(int(time.time() * 1000))

    params = {
        'method':'list',
        'djjg':'',
        'random':random
    }

    data = {
        'currentPageNo':1,
        'yzm':checkCode,
        'maent.entname':name
    }

    response = url_requests.post(url=url,
                                 params=params,
                                 data=data,
                                 headers=headers,
                                 cookies=cookies)
    html = response.text
    # print html
    soup = BeautifulSoup(html, 'lxml')
    list = soup.find_all('li',{'class':'font16'})
    if len(list) == 0:
        return None

    for each in list:
        href = each.a['onclick'].split("'")
        htmlId.append(href[1])

    return htmlId


def main(**kwargs):
    """主流程函数

    :params: name， 企业名称
    :type: unicode
    """

    company = kwargs.get('name').encode('GBK')

    # 获取cookies
    cookie = get_cookie()

    # 获取验证码Image对象
    img = get_image(cookie)

    # 识别验证码结果（jg）
    jg = get_check(img)

    # 返回对应企业名的id  type: list
    id = get_query(company, jg, cookie)

    return id



if __name__ == '__main__':

    company = '腾讯'

    print main(name=company)