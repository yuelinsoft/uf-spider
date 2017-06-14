# -*- coding:utf-8 -*-
import requests
import re
import os
from io import BytesIO
from PIL import Image
from ImgR.CheckCode import *

session = requests.Session()
# ——————————————————————————————————————————
def two_Value(img):
    x, y = img.size
    # 将上下边三行像素点的颜色清除
    img_RGB = img.convert('RGB')
    for i in range(x):
        for j in range(3):
            img_RGB.putpixel((i, j), (255,255,255))
        for z in range(47,50):
            img_RGB.putpixel((i, z), (255,255,255))

    img_HSV = img_RGB.convert('HSV')
    for i in range(0, x):
        S0 = 0
        for j in range(3, y - 3):
            H, S, V = img_HSV.getpixel((i, j))
            # print H, S, V, '(', i, j, ')'
            S0 = S0 + S
            # print S0 / 44
        for j in range(3, y - 3):
            H, S, V = img_HSV.getpixel((i, j))
            if S > (S0 / 44 - 16):
                img_RGB.putpixel((i, j), (255, 255, 255))
            else:
                img_RGB.putpixel((i, j), (0, 0, 0))
    # 降噪处理
    img_RGB = clear(img_RGB, 2, 1)
    # img_RGB.show()

    return img_RGB

def cut(image):
    one = image.crop((30,0,60,50))
    two = image.crop((60,0,90,50))
    three = image.crop((110,0,140,50))
    # one.show()
    # two.show()
    # three.show()

    return one, two, three

path = 'E:\\Py_project\\QYXX\\ZheJiang\\'
trainx, trainy = loadTrainSet(path + 'trainSet\\')

def classify(image):
    '''
    识别主函数了
    :param image:
    :return:
    '''
    image = two_Value(image)

    one, two, three = cut(image)

    s_one = classify_SVM(trainx, trainy, one)
    s_two = classify_SVM(trainx, trainy, two)
    s_three = classify_SVM(trainx, trainy, three)
    try:
        if s_two == '+':
            result = int(s_one) + int(s_three)
        elif s_two == '-':
            result = int(s_one) - int(s_three)
        else:
            result = int(s_one) * int(s_three)
    except:
        result = None

    return result

def check(image):
    '''
    边缘检测，是否是算术
    :param image:
    :return:
    '''
    image = two_Value(image)
    w, h = image.size
    for x in range(w):
        for y in range(h):
            px = image.getpixel((x, y))
            if px == 0 and x < 10:
                return 0
            else:
                return 1

# ——————————————————————————————————————————

# 获取cookies值
def get_cookie():
    url = 'http://gsxt.zjaic.gov.cn/zhejiang.jsp'
    headers = {
        'Host':'gsxt.zjaic.gov.cn',
        'Referer':'http://gsxt.saic.gov.cn/',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    response = session.get(url, headers=headers, timeout=10)
    cookie = dict(response.cookies)

    return cookie

# 获取验证码，暂时需要手动输入
def get_checkCode(cookie):
    url = 'http://gsxt.zjaic.gov.cn/common/captcha/doReadKaptcha.do'
    headers = {
        'Host': 'gsxt.zjaic.gov.cn',
        'Referer': 'http://gsxt.zjaic.gov.cn/zhejiang.jsp',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }

    response = session.get(url, headers=headers,cookies=cookie)
    if response.status_code == 403:
        print u'请求遇到了403错误，请检查网络是否被封IP。'
        os._exit(0)
    f = BytesIO(response.content)
    img = Image.open(f)
    # img.show()
    if check(img) == 0:
        return get_checkCode(cookie)
    # checkCode = raw_input(u'手动输入验证码：')
    checkCode = classify(img)
    # print checkCode
    return checkCode

# 返回企业对应的id
def get_Id(name):
    '''
    :param name: 企业名称  带u的
    :return:
    '''
    url = 'http://gsxt.zjaic.gov.cn/search/doGetAppSearchResult.do'
    headers = {
        'Host': 'gsxt.zjaic.gov.cn',
        'Origin': 'http://gsxt.zjaic.gov.cn',
        'Referer': 'http://gsxt.zjaic.gov.cn/zhejiang.jsp',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }

    #
    t = 0
    id = None
    while t < 20:
        # 调用get_cookie函数获取cookies
        cookies = get_cookie()
        # 调用get_checkCode函数获取验证码
        checkCode = get_checkCode(cookies)
        # 拼出data
        data = {
            'clickType': 1,
            'verifyCode': checkCode,
            'name': name
        }

        response = session.post(url, data=data, headers=headers, cookies=cookies, timeout=10)
        html = response.text

        id = re.findall('corpid=(.*?)"', html, re.S)
        if len(id) != 0:
            return id[0]
        t += 1
        print u'验证码输入错误，请重试。'

    return id

# 由于一个id具有时效性，所以将本py文件作为库加载到zhejiang_data.py中 from zhejiang_query import *
if __name__ == '__main__':

    id = get_Id(u'海盐溢利自攻螺钉厂')

    print id