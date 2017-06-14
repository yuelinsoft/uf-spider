# -*- coding:utf-8 -*-

'''跟四川的共用同一个训练集'''
__author__ = 'lijb'

import time
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from common.CheckCode import *

session = requests.Session()

def get_cookie():

    url = 'http://xygs.snaic.gov.cn/ztxy.do'
    random = str(int(time.time() * 1000))   # 13位的时间戳
    params = {'method':'index','random':random}
    headers = {
        'Host':'xygs.snaic.gov.cn',
        'Referer': 'http://xygs.snaic.gov.cn',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    t = 0
    cookie = None
    while t < 20:
        try:
            response = session.get(url, params=params, headers=headers)
            cookie = dict(response.cookies)
            break
        except:
            print u'悲剧了！网络不是很好，第', t, u'次尝试get_cookie……'
            t += 1
            continue

    return cookie

def get_image(cookies):
    '''
    :return: 验证码image对象
    '''
    URL = 'http://xygs.snaic.gov.cn/ztxy.do'
    headers = {
        'Host': 'xygs.snaic.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    random = str(int(time.time() * 1000))
    params = {
        'method':'createYzm',
        'dt':random,
        'random':random
    }
    response = None
    t = 0
    while t < 20:
        t += 1
        try:
            response = session.get(URL, headers=headers, params=params,cookies=cookies,timeout=20)
            break
        except:
            print u'悲剧了！网络不是很好，第', t, u'次尝试get_image……'
            t += 1
            continue
    file = BytesIO(response.content)
    im = Image.open(file)
    return im

def cut_threeImg(Image):
    '''
    :param Image: 二值image对象
    :return: three images
    '''
    one = Image.crop((0,0,16,30))
    two = Image.crop((16,0,33,30))
    three = Image.crop((33,0,48,30))

    return one, two ,three

def get_check(Image):
    # 跟四川的共用同一个训练集
    trains, labels = loadTrainSet('../train_opreator/f2_sichuan_train_opeator.csv')
    # 二值化
    img = twoValueImage(Image, 120)
    # 切出三个来
    imgs = cut_threeImg(img)
    images = []
    for each in imgs:
        each = cutAround(each)
        each = formatImg(each, (20, 20))
        images.append(each)
    one = classify_SVM(trains, labels, images[0])
    two = classify_SVM(trains, labels, images[1])
    three = classify_SVM(trains, labels, images[2])
    if two == '+':
        jg = int(one) + int(three)
    else:
        jg = int(one) * int(three)

    return jg

def get_htmlId(name, checkCode, cookies):
    '''
    :param name: 公司名
    :param checkCode: 验证码
    :param cookies: cookie
    :return: 搜索结果的url的id参数列表
    '''
    url = 'http://xygs.snaic.gov.cn/ztxy.do'
    headers = {
        'Host':'xygs.snaic.gov.cn',
        'Origin':'http://xygs.snaic.gov.cn',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    random = str(int(time.time() * 1000))
    params = {
        'method':'list',
        'djjg':'',
        'random':random,
        'yourIp':'58.60.39.107'
    }
    data = {
        'currentPageNo':1,
        'yzm':checkCode,
        'maent.entname':name
    }
    response = session.post(url,params=params,data=data, headers=headers,cookies=cookies,timeout=20)
    html = response.text
    # print html
    soup = BeautifulSoup(html, 'lxml')
    list = soup.find_all('li',{'class':'font16'})
    if len(list) == 0:

        return None
    htmlId = []
    for each in list:
        href = each.a['onclick'].split("'")
        htmlId.append(href[1])

    return htmlId

def mainId(name):
    '''
    :param name: unicode name
    :return:
    '''
    # 转换成gb2312的urlencode编码
    na = name.encode('gb2312')
    id = None
    # 此处循环是因为找不到结果有可能是真的没有，也有可能是验证码识别错误，10次循环以保证验证码能识别成功
    t = 0
    while t < 10:
        cookie = get_cookie()
        img = get_image(cookie)
        jg = get_check(img)
        id = get_htmlId(na, jg, cookie)
        if id != None:
            break
        else:
            print u'您搜索的条件无查询结果,可能是验证码识别错误，也可能是真的没结果。重试ing'
            t += 1

    return id


if __name__ == '__main__':

    name = [u'陕西宇伟物资有限公司',
            u'陕西福盛兴医药有限公司',
            u'陕西益力德电力工程有限公司']

    id = mainId(name[2])
    print id