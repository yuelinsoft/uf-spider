# -*- coding:utf-8 -*-
__author__ = 'lijb'

import requests
from PIL import Image
from bs4 import BeautifulSoup
import operator
import pytesseract
from difflib import SequenceMatcher
from io import BytesIO

# 创建一个Session会话
session = requests.Session()

# ******下面是识别部分************
# 获取cookie
def get_cookies():
    '''
    :return: cookies for get_image
    '''
    url = 'http://gsxt.xzaic.gov.cn/search.jspx'
    headers = {
        'Host': 'gsxt.xzaic.gov.cn',
        'Referer': 'http://gsxt.xzaic.gov.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    cookies = None
    t = 0
    while t < 20:
        t += 1
        try:
            response = session.get(url, headers=headers, timeout=20)
            cookies= dict(response.cookies)
            break
        except:
            print u'悲剧了！网络不是很好，第', t, u'次尝试get_cookie……'
            continue

    return cookies

# 用cookie获取验证码，返回Image对象
def get_image(cookies):
    '''
    :return: 验证码image对象
    '''
    URL = 'http://gsxt.xzaic.gov.cn/validateCode.jspx'
    headers = {
        'Host': 'gsxt.xzaic.gov.cn',
        'Referer': 'http://gsxt.xzaic.gov.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    params = {
        'type': 1,
        'id': ''
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
            continue
    file = BytesIO(response.content)
    img = Image.open(file)

    return img

# 识别验证码返回识别结果
def get_stings(im):
    '''
    :param im: Image 对象
    :return: 识别后的结果
    '''
    with open('dictory.txt', 'r') as f3:
        # 成语库
        dictory = f3.readlines()

    w,h = im.size
    for y in range(h):
        for x in range(w):
            pixel = im.getpixel((x, y))
            if sum(pixel)/3 >225:
                im.putpixel((x, y), (0, 0, 0))
            else:
                im.putpixel((x,y),(255,255,255))
    string = pytesseract.image_to_string(im,lang='chi_sim',config ='-psm 7').strip().replace('夭','天').replace('\\','一').replace(',','').replace('，','').replace("'",'').replace('v','').replace('又寸','对').replace('白勺','的').replace('女子','好').replace('弓虽','强').replace('i炎','谈')
    rank_dic = {}
    for a in dictory:
        a = a.replace('\n','')
        ratio = SequenceMatcher(None,a,string).ratio()
        if ratio > 0:
            rank_dic.update({a : ratio})
    try:
        string = max(rank_dic.items(),key=operator.itemgetter(1))[0]
    except:
        string = None

    return string

# ******根据验证码识别结果获取对应企业的Id，返回list************
def get_htmlId(name, checkCode, cookies):
    '''
    :param name: 公司名
    :param checkCode: 验证码
    :param cookies: cookie
    :return: 搜索结果的url的id参数列表
    '''
    url = 'http://gsxt.xzaic.gov.cn/searchList.jspx'
    headers = {
        'Origin':'http://gsxt.xzaic.gov.cn',
        'Referer':'http://gsxt.xzaic.gov.cn/search.jspx',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }

    data = {
        'checkNo': checkCode,
        'entName': name
    }
    response = session.post(url,data=data, headers=headers,cookies=cookies,timeout=20)
    html = response.text

    soup = BeautifulSoup(html, 'lxml')
    list = soup.find_all('li',{'class':'font16'})
    if len(list) == 0:
        print u'您搜索的条件无查询结果。'
        return None
    htmlId = []
    for each in list:
        href = each.a['href'][-32:]
        htmlId.append(href)

    return htmlId

def mainId(name):
    '''
    该函数的功能是调用上面的函数，返回对应name的ID
    :param name: 所搜企业名称
    :return: 所搜企业名称的ID
    '''
    # 获取cookie
    cookie = get_cookies()
    # 获取验证码Image对象
    img = get_image(cookie)
    # 识别出验证码
    checkCode = get_stings(img)
    # 返回对应企业的ID列表
    IdList = get_htmlId(name, checkCode, cookie)

    return IdList

name = [u'西藏藏旅通途网络科技有限公司',
        u'西藏祥源旅行社有限公司',
        u'西藏昶建商务服务有限公司',
        u'西藏仙草生物科技有限公司',
        u'西藏有限公司']

print mainId(name[4])