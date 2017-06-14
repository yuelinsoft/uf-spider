# -*- coding:utf-8 -*-
# author: 'KEXH'
from __future__ import unicode_literals
from EnterpriseCreditCrawler.common import captcha, common
import requests
from PIL import Image
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO
Session = requests.Session()
result = {}

'''
拿cookies，img string，name-get html-link
'''

# def get_cookies():
#     main_url = "http://gxqyxygs.gov.cn/search.jspx"
#     headers = {
#         'Accept': 'image/png,image/*;q=0.8,*/*;q=0.5',
#         'Accept-Encoding': 'gzip, deflate',
#         'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
#         'Connection': 'keep-alive',
#         'Host': 'gxqyxygs.gov.cn',
#         'Referer': 'http://gxqyxygs.gov.cn/search.jspx',
#         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
#                 }
#     html = Session.get(url=main_url, headers=headers, timeout=10)
#     cookies_code = dict(html.cookies)
#     print cookies_code
#     return cookies_code

def get_image(cookies):
    url = "http://gxqyxygs.gov.cn/validateCode.jspx?type=1&id=0.5803961064875148"
    headers = {
        'Host': 'gxqyxygs.gov.cn',
        'Referer': 'http://gxqyxygs.gov.cn/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }
    params = {
        'id': '0.5803961064875148',
        'type': '2'
            }
    html = Session.get(url=url,
                       headers=headers,
                       params=params,
                       cookies=cookies,
                       proxies=_proxies,
                       timeout=10)
    imgFile = BytesIO(html.content)
    im = Image.open(imgFile)
    # im.show()
    # path = "F:\\material\\Pics\\" + "0617.jpg"
    # im.save(path)
    return im

def replaceStr(s):
    dict = {
        '夭': '天',
        '\\': '一',
        ',': '',
        '，': '',
        "'": '',
        'v': '',
        '又寸': '对',
        '白勺': '的',
        '女子': '好',
        '弓虽': '强',
        'i炎': '谈'
            }
    for d in dict:
        s = s.replace(d, dict[d])
    return s

def get_html(name, string, cookies):
    # check_url = 'http://gxqyxygs.gov.cn/checkCheckNo.jspx'
    # headers = {
    #         'Host': 'gxqyxygs.gov.cn',
    #         'Referer': 'http://gxqyxygs.gov.cn/search.jspx',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
    #         'X-Requested-With': 'XMLHttpRequest'
    #     }
    # data = {'checkNo': string}
    # check_html = Session.post(url=check_url, headers=headers, data=data, cookies=cookies, timeout=10)
    # print check_html.text# "{success:true}"
    search_url='http://gxqyxygs.gov.cn/searchList.jspx'
    headers = {
        'Host': 'gxqyxygs.gov.cn',
        'Referer': 'http://gxqyxygs.gov.cn/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }
    data = {
            'checkNo': string,
            'entName': name
            }
    search_html = Session.post(url=search_url,
                               headers=headers,
                               data=data,
                               proxies=_proxies,
                               timeout=10)
    content = search_html.content
    return content

def main(**kwargs):
    name = kwargs.get('name')
    global _proxies
    _proxies = kwargs.get('proxies')
    # cookies = get_cookies()
    cookies = {}
    im = get_image(cookies)
    string = captcha.get_string(im)
    listPage = get_html(name, string, cookies)
    result_list = common.parse_url(listPage, 'li','font16')
    # print result_list
    if result_list == None:
        return main(name=name)
    else:
        return result_list


if __name__ == '__main__':

    name = '腾讯'
    main(name=name)


