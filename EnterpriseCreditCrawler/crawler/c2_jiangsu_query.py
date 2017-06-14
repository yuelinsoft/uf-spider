# -*- coding:utf-8 -*-
"""
    __author__ = 'lijb'

    该脚本封装了两个函数：
    1、image_to_string函数，来返回验证码（字符串）
    2、main函数，内封装了三个函数通过依次调用，最终返回用于访问data脚本的参数。

"""

from __future__ import unicode_literals
import json
import pytesseract
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
from EnterpriseCreditCrawler.common import url_requests
from io import BytesIO
from PIL import Image
from EnterpriseCreditCrawler.common.uf_exception import RequestError


times = 0   # 验证码识别次数上限

def image_to_string(image):
    """二值化图片并返回识别后的字符串

    :param image: image对象
    :return:
    """
    w,h = image.size
    im = image.convert('L')
    for y in range(h):
        for x in range(w):
            pixel = im.getpixel((x, y))
            if pixel >175:
                im.putpixel((x, y), 255)
            else:
                im.putpixel((x,y),0)
    # im.show()
    string = pytesseract.image_to_string(im,lang='eng',
                                         config ='-psm 7')
    # print string
    return string

def main(**kwargs):
    """include three function

    :return: params for c2_jiangsu_data.py
    """

    search_key = kwargs.get('name')
    proxies = kwargs.get('proxies')
    # proxies = None  # 暂时不使用代理IP
    def get_cookies():
        """获取首页的cookies

        :return: cookies
        """
        url = 'http://www.jsgsj.gov.cn:58888/province/'
        headers = {
            'Host': 'www.jsgsj.gov.cn:58888',
            'X-Forwarded-For': '8.8.8.8',
            'Referer': 'http://gsxt.saic.gov.cn/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/44.0.2403.155 Safari/537.36'
        }
        response = url_requests.get(url=url, headers=headers,
                                    proxies=proxies, timeout=20)

        cookies = dict(response.cookies)

        return cookies

    # 返回cookies，并作为下面三个函数的全局变量
    cookies = get_cookies()

    def get_checkCode():
        """用cookies获取验证码并识别成字符串

        :return: string
        """
        captcha_url = 'http://www.jsgsj.gov.cn:58888/province/rand_img.jsp'
        headers = {
            'X-Forwarded-For': '8.8.8.8',
            'Host': 'www.jsgsj.gov.cn:58888',
            'Referer': 'http://www.jsgsj.gov.cn:58888/province/',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/44.0.2403.155 Safari/537.36')
        }

        html = url_requests.get(url=captcha_url,
                                headers=headers,
                                cookies=cookies,
                                proxies=proxies,
                                timeout=20).content

        file = BytesIO(html)
        im = Image.open(file)
        checkCode = image_to_string(im)

        return checkCode

    def get_param1():
        """校验验证码，并返回一个name参数，用作下一次访问。

        :return: name
        """

        global times


        checkCode = get_checkCode()

        url = ('http://www.jsgsj.gov.cn:58888/province'
                       '/infoQueryServlet.json?checkCode=true')
        headers = {
            'X-Forwarded-For': '8.8.8.8',
            'Host': 'www.jsgsj.gov.cn:58888',
            'Origin': 'http://www.jsgsj.gov.cn:58888',
            'Referer': ('http://www.jsgsj.gov.cn:58888/province'
                        '/login.jsp'),
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/44.0.2403.155 Safari/537.36')
        }
        data = {
            'name': search_key,
            'verifyCode': checkCode
        }
        try:
            json_data = url_requests.post(url=url,
                                          headers=headers,
                                          data=data,
                                          cookies=cookies,
                                          proxies=proxies,
                                          timeout=20).text
            id_tag = json.loads(json_data)

            return id_tag['bean']['name']
        except:
            print '江苏省验证码识别错误，正在尝试重试……'.encode('utf-8')
            times += 1
            # print times
            if times < 19:
                return get_param1()
            else:
                raise RequestError("验证码识别失败，请稍后重查。".encode('utf-8'))

    def get_param2():
        """用检验验证码时返回的name参数，再访问，得结果。

        :return: 搜索结果列表
        """

        url = ('http://www.jsgsj.gov.cn:58888/province/infoQueryServlet.json'
               '?queryCinfo=true ')
        headers = {
            'Host': 'www.jsgsj.gov.cn:58888',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.71 Safari/537.36')
        }

        name = get_param1()

        data = {
            'name': name,
            'searchType': 'qyxx',
            'pageNo': 1,
            'pageSize': 10
        }

        json_data = url_requests.post(url=url,
                                      headers=headers,
                                      data=data,
                                      cookies=cookies,
                                      proxies=proxies,
                                      timeout=20).text

        id_tag = json.loads(json_data)
        if id_tag.has_key('items'):
            result_list = []
            for each_item in id_tag['items']:
                item = {}
                item['company'] = each_item['CORP_NAME']
                item['detail'] = each_item
                result_list.append(item)
            return result_list
        else:
            return get_param2()

    return get_param2()


if __name__ == '__main__':
    name = ['江苏汇远房地产发展有限责任公司',  # 分支机构， 股东出资， 主要人员， 抽查检查，等
            '丸悦（无锡）商贸有限公司',        # 行政处罚
            '江苏省伟宇塑业有限公司',          # 动产抵押
            ]
    print main(name=name[1])




