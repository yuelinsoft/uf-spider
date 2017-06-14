# -*- coding:utf-8 -*-

__author__ = 'lijb'

import requests
from bs4 import BeautifulSoup
from io import BytesIO

# ——————————黄金分割线————验证码识别库————

from EnterpriseCreditCrawler.common.captcha import *

session = requests.Session()

# 按指定坐标切成四大块
def cut_four(image):
    '''
    :param image: Image对象（通常是二值图）
    :return: 四个Image对象
    '''
    one = image.crop((30,0,60,50))
    two = image.crop((60,0,90,50))
    three = image.crop((90, 0, 120, 50))
    four = image.crop((120, 0, 150, 50))

    return one, two, three, four

#———————————黄金分割线————————————————————

def get_cookies_ticket():
    '''
    不传任何参数，从首页中获取cookies, credit_ticket
    :return:
    '''
    url = 'http://qyxy.baic.gov.cn/beijing'
    headers = {
        'Host':'qyxy.baic.gov.cn',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }

    cookie = None; credit_ticket = None
    t = 0
    while t < 10:
        try:
            html = session.get(url, headers=headers, timeout=20)

            cookie = dict(html.cookies)

            soup = BeautifulSoup(html.text, 'lxml')

            credit_ticket = soup.find('input', {'id': 'credit_ticket'})['value']
            break
        except:
            t += 1
            print u'获取cookies，credit_ticket失败，第', t, u'次尝试……'

    return cookie, credit_ticket

def get_checkCode(cookies):

    url = 'http://qyxy.baic.gov.cn/CheckCodeCaptcha?num=00'
    headers = {
        'Host': 'qyxy.baic.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    re = session.get(url, cookies=cookies, headers=headers, timeout=20)
    image = BytesIO(re.content)
    image = Image.open(image)

    # 二值
    image = twoValueImage(image, 140)
    # 降噪
    image = clear(image,4,2)
    # 切割
    images = cut_four(image)
    # 识别并组合
    trainX, trainY = loadTrainSet('../train_operator/a1_beijing_train_operator.csv')
    code = ''
    for i in range(4):

        s = classify_SVM(images[i], trainX, trainY)
        code = code + s

    return code

def get_paramsList(data, cookies):
    '''
    :param data: post请求的data
    :param cookies: cookies
    :return: 搜索结果的集合，包含dict的list，其dict是用于请求企业信息主界面的params
    '''
    url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml'

    headers = {
        'Host':'qyxy.baic.gov.cn',
        'Origin':'http://qyxy.baic.gov.cn',
        'Referer':'http://qyxy.baic.gov.cn/beijing',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    try:
        res = session.post(url, data=data, headers=headers, cookies=cookies, timeout=20)
    except:
        print u'超时重试……'
        return None
    soup = BeautifulSoup(res.text, 'lxml')
    # 找到所有结果
    list = soup.find_all('li', {'class': 'font16'})
    if len(list) == 0:
        return None
    paramsList = []   # 将所有结果保存在列表里 [{},{},{}] 这种形式
    params = {}
    for each in list:
        info = each.a['onclick']

        params['entId'] = info.split("'")[3]
        params['credit_ticket'] = info.split("'")[7]
        params['entNo'] = info.split("'")[5]

        paramsList.append(params)
    # 若搜索结果只有一条，使用的时候应该是带个下标 0 ，如：  params = get_data(data)[0]
    return paramsList

# 主流程函数
def mainP(name):
    '''
    主流程函数
    :return: paramsList
    '''
    t = 0
    paramsList = None
    while t < 10:
        # 获取data中credit_ticket对应的值
        cookies, credit_ticket = get_cookies_ticket()

        # 接着获取验证码并识别
        checkCode = get_checkCode(cookies)

        # 组合出data
        data = {
            # 'currentTimeMillis': str(int(time.time() * 1000)),
            'credit_ticket': credit_ticket,
            'checkcode': checkCode,
            'keyword': name
        }

        # 关键函数
        paramsList = get_paramsList(data, cookies)
        if paramsList != None:
            break
        else:
            print u'您搜索的条件无查询结果,可能是验证码识别错误，也可能是真的没结果。重试ing'
            t += 1

    return paramsList

# openEntInfo('深圳前海融金所投资管理有限公司北京分公司','20e38b8b4e85c580014e8b59107d7516','110105019487856', '57C0E302749FCB98ABC795E600AED3A6');

if __name__ == '__main__':
    name = [u'北京紫晶立方科技有限公司',   #股东信息 与 变更信息翻页
            ]

    x = mainP(name[0])
    print x