# -*- coding:utf-8 -*-

__author__ = 'lijb'

import requests
from bs4 import BeautifulSoup
from io import BytesIO

# 创建一个Session会话
session = requests.Session()

# get_Cookies 跟 get_Image 共用的http请求头
headers = {
    'Host': 'wsgs.fjaic.gov.cn',
    'Referer': 'http://gsxt.saic.gov.cn/',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
}

# ——————————黄金分割线————验证码识别部分————

from common.CheckCode import *

def cutFour(image):
    one = image.crop((0, 0, 40, 53))
    two = image.crop((40, 0, 80, 53))
    three = image.crop((80, 0, 120, 53))
    four = image.crop((120, 0, 160, 53))

    return one, two, three, four

def shibie(img, trainx, trainy):
    img = twoValueImage(img, 200)
    img = clear(img, 4, 5)
    one, two, three, four = cutFour(img)
    x1 = classify_SVM(trainx, trainy, one)
    x2 = classify_SVM(trainx, trainy, two)
    x3 = classify_SVM(trainx, trainy, three)
    x4 = classify_SVM(trainx, trainy, four)
    string = x1 + x2 + x3 + x4

    return string

#———————————黄金分割线————————————————————

# 获取福建省的cookie
def get_Cookies_token():
    '''
    :return: Cookies,token
    '''
    # 福建首页
    url = 'http://wsgs.fjaic.gov.cn/creditpub/home'

    cookie = None
    token = None
    t = 0
    while t < 20:
        t += 1
        try:
            response = session.get(url, headers=headers, timeout=20)
            cookie = dict(response.cookies)
            soup = BeautifulSoup(response.text, 'lxml')
            token = soup.find('input', {'name': 'session.token'})['value']
            break
        except:
            print u'悲剧了！网络不是很好，第', t, u'次尝试get_Cookie……'
            continue

    return cookie, token

# 获取验证码的Image对象
def get_Image(cookies):
    '''
    :param cookies: 对应省份（福建）的cookies
    :return: 验证码Image对象
    '''
    # 验证码网址
    url = 'http://wsgs.fjaic.gov.cn/creditpub/captcha?preset=01'

    response = None
    t = 0
    while t < 20:
        t += 1
        try:
            response = session.get(url, headers=headers, cookies=cookies, timeout=20)
            break
        except:
            print u'悲剧了！网络不是很好，第', t, u'次尝试get_image……'
            continue

    file = BytesIO(response.content)
    img = Image.open(file)

    return img

# 识别验证码返回识别结果
def get_string(image):
    '''
    :param image: 验证码Image对象
    :return: 识别结果
    '''
    w, h = image.size
    for y in range(h):
        for x in range(w):
            pixel = image.getpixel((x, y))
            if sum(pixel) / 3 > 225:
                image.putpixel((x, y), (255, 255, 255))
            else:
                image.putpixel((x, y), (0, 0, 0))

    # —————————————识别——————————————————

    trainx, triany = loadTrainSet('../train_opreator/c5_fujian_train_opeator.csv')
    string = shibie(image,trainx, triany)

    # ——————————————————————————————————————————————

    return string

# 获取搜索结果的id
def get_Id(name, checkCode, cookies, token):

    url = 'http://wsgs.fjaic.gov.cn/creditpub/search/ent_info_list'

    # http请求头
    headers = {
        'Host':'wsgs.fjaic.gov.cn',
        'Origin':'http://wsgs.fjaic.gov.cn',
        'Referer':'http://wsgs.fjaic.gov.cn/creditpub/home',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    # post请求的数据
    data = {
        'searchType': 1,
        'captcha': checkCode,
        'session.token': token,
        'condition.keyword':name
    }
    if checkCode == None:
        return None
    try:
        # 验证码识别错误时，这里会报错
        response = session.post(url, headers=headers, data=data, cookies=cookies,timeout=20)
        soup = BeautifulSoup(response.text, 'lxml')
        link = soup.find('div', {'class': 'link'}).a['href']
        if len(link) == 0:
            print u'您搜索的条件无查询结果,可能是验证码识别错误，也可能是真的没结果。'
            return None
        Id = link[-39:-7]
    except:
        print u'验证码识别错误'
        Id = None

    return Id


def mainId(name):
    '''
    :param name: 企业名称，unicode编码
    :return: 企业对应的id
    '''
    Id = None
    # 此处循环是因为找不到结果有可能是真的没有，也有可能是验证码识别错误，10次循环以保证验证码能识别成功
    t = 0
    while t < 20:
        # cookies = cookie[0], token = cookie[1]
        cookie = get_Cookies_token()

        # Image = get_Image(cookie[0])

        # 网站的bug，目前把验证码写死，也能拿到对应的id，若后续此bug修复，取消上下两行注释即可
        # checkCode = get_string(Image)

        Id = get_Id(name, 'aaaa', cookie[0], cookie[1])
        if Id != None:
            break
        else:
            t += 1
            print t

    return Id

if __name__ == '__main__':

    name = [u'福州强东贸易有限公司',
            u'福建慧智和诚文化发展有限公司',
            u'福州国姓爷餐饮管理有限公司']

    id = mainId(name[0])
    print id
