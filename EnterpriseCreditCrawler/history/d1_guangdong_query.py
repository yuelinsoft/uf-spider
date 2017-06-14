# -*- coding:utf-8 -*-
"""
    __author__ = "lijianbin"

    广东省企业信用查询脚本
"""


from __future__ import unicode_literals
import os
import json
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import RequestError
from EnterpriseCreditCrawler.common.captcha import (cutAround, clear,
                                                    classify_SVM, formatImg,
                                                    loadTrainSet)



def word(image):
    '''获取每个字的像素值以及对应的位置，保存在字典中。

    :param image: 原始验证码图片Image对象
    :return: example {像素值：该像素值所在的位置（起始值是1，0为背景色）}
    '''

    image = image.convert('RGB')
    w, h = image.size
    countA = {}  # {像素值：该像素值的数量}
    countB = {}  # {像素值：该像素值所在的位置（起始值是1，0为背景色）}
    t = 0  # 记录位置
    for x in range(w):
        for y in range(h):
            g = image.getpixel((x, y))
            countA[g] = countA.get(g, 0) + 1
            while countB.has_key(g) == False and countA[g] > 100:
                countB[g] = t
                t += 1

    return countB

def cut_union(image, G):
    '''根据具体的像素值进行二值化（只对每个字颜色一致的验证码有效）

    :param image:
    :param G: RGB阈值
    :return:
    '''
    image = image.convert('RGB')
    w, h = image.size
    for x in range(w):
        for y in range(h):
            g = image.getpixel((x, y))
            if g == G:
                image.putpixel((x, y), (0, 0, 0))
            else:
                image.putpixel((x, y), (255, 255, 255))
    # image.show()
    return image

def main_check(image, trainX, trainY):
    '''验证码识别主函数

    :param image: 原始图
    :param trainX: 训练样本
    :param trainY: 样本标签
    :return: 识别结果——int
    '''

    words = word(image)
    # 不论是否是成语，找出前四个字的像素值
    G1, G2, G3, G4 = 0, 0, 0, 0
    for each in words.keys():
        if words[each] == 1:
            G1 = each
        elif words[each] == 2:
            G2 = each
        elif words[each] == 3:
            G3 = each
        elif words[each] == 4:
            G4 = each
        else:
            continue
    union = [G1, G2, G3, G4]
    union_image = [] # 依次存放单个字的image对象
    for each in union[:-1]:
        img = cut_union(image, each)    # 切出单个
        img = clear(img, 2, 1)          # 去噪点
        img = cutAround(img)            # 环切出单个字
        img = formatImg(img, (30,30))   # 重定义单个字的尺寸
        # img.show()
        jg = classify_SVM(img, trainX, trainY)
        union_image.append(jg)
    try:
        if union_image[1] == '+':
            result = int(union_image[0]) + int(union_image[2])
        elif union_image[1] == '-':
            result = int(union_image[0]) - int(union_image[2])
        else:
            result = int(union_image[0]) * int(union_image[2])
    except ValueError: # 可能会将数字识别成运算符
        result = None

    return result

'''—————————————————上面是验证码识别所用的函数———————————————————————————'''

def get_cookie():
    """访问验证码,获取cookies值

    :return:
    """
    url = 'http://gsxt.gdgs.gov.cn/aiccips/verify.html'

    headers = {
        'Host':'gsxt.gdgs.gov.cn',
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/52.0.2743.116 Safari/537.36')
    }

    res = url_requests.get(url, headers=headers, timeout=20)

    cookie = dict(res.cookies)

    return cookie

# 获取验证码
def get_checkCode(cookie):
    """返回验证码识别结果

    :param cookie:
    :return:
    """

    url = 'http://gsxt.gdgs.gov.cn/aiccips/verify.html'

    headers = {
        'Host': 'gsxt.gdgs.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/52.0.2743.116 Safari/537.36')
    }

    response = url_requests.get(url, headers=headers, cookies=cookie,
                                timeout=20)
    if response.status_code == 403:
        raise RequestError('请求遇到了403错误，请检查网络是否被封IP。')

    f = BytesIO(response.content)
    img = Image.open(f)
    # img.show()
    # 判断是否是成语
    words = word(img)
    if len(words) <= 5:  # 是成语，则4个都用上
        print '验证码为成语，跳过重新获取……'
        return get_checkCode(cookie)
    else:  # 是算术，则只需要用前三个
        return img

def main(**kwargs):
    """主函数， 被总控调用， 不得随意更改名称。

    :param kwargs: name=企业名称
    :return:
    """

    company_name = kwargs.get('name')
    # 获取访问验证码时的cookies
    cookies = get_cookie()

    # 加载训练集(相对路径转绝对路径)
    path_a = os.path.dirname(__file__)
    path_a = os.path.abspath(os.path.join(path_a, '..'))
    abs_path = os.path.join(path_a,
                            'train_operator/d1_guangdong_train_operator.csv')

    trainX, trainY = loadTrainSet(abs_path)
    image = get_checkCode(cookies)
    code = main_check(image, trainX, trainY)
    if code == None: # 如果数字被识别成运算符，则回调main重来
        return main(name=company_name)
    # print code

    # 先访问这个网站获取到 textfield
    url = 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/checkCode.html'
    data = {
        'textfield': company_name,
        'code': code
    }
    headers = {
        'Host': 'gsxt.gdgs.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/47.0.2526.73 Safari/537.36'),
        'Referer': 'http://gsxt.gdgs.gov.cn/'
    }
    response = url_requests.post(url, headers=headers, data=data,
                                 cookies=cookies, timeout=10)
    if response != None:
        if 'textfield' in response.text:
            textfield = json.loads(response.text)['textfield']
            # print textfield
        else:
            print '验证码识别错误'
            return main(name=company_name)

        # 再用 textfield 参数，访问下面的网址，获取搜索结果（企业列表）
        url = 'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo.html '
        data = {
            'textfield': textfield,
            'code': str(code)
        }
        response = url_requests.post(url, headers=headers, data=data,
                                     cookies=cookies, timeout=10)
        if response != None:
            html = response.content
            soup = BeautifulSoup(html, 'lxml')
            list = soup.find_all('li', class_='font16')
            link_list = []
            for each in list:
                link = each.a['href'].decode('utf-8') # 为了统一unicode编码，
                if '..' in link:
                    link = 'http://gsxt.gdgs.gov.cn/aiccips' + link[2:]
                link_list.append(link)
            # print link_list
            return link_list
    else:
        return main(name=company_name)

if __name__ == '__main__':

    name = ['融金所',
            '腾讯',
            '广州腾讯科技有限公司',
            '王尼玛',
            '深圳市华星光电技术有限公司',
            '江门市蓬江区庆圆美食坊'
            ]

    main(name=name[-3])
