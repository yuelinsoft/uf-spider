# -*- coding: utf-8 -*-

"""
    从总入口，不分省份
"""

from __future__ import unicode_literals
import time
import json
from io import BytesIO
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.slide_check_code_recognition \
     import get_validate_data_based_online
from EnterpriseCreditCrawler.common.uf_exception import (CaptchaFailed)



def get_gt_challenge():
    """获取gt和challenge参数，滑快验证码需要用到的。"""

    url = 'http://www.gsxt.gov.cn/SearchItemCaptcha'
    headers = {
        'Host': 'www.gsxt.gov.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': url_requests.random_userAgent(),
        'Referer': 'http://www.gsxt.gov.cn/index.html'
    }
    params = {
        'v': int(time.time() * 1000)
    }

    response = url_requests.get(url=url, params=params,
                                headers=headers, proxies=proxies)

    data = json.loads(response.content)
    gt = data.get('gt')
    challenge = data.get('challenge')

    return gt, challenge

def get_path(gt):
    """获取验证码所需要用到的path参数"""

    url = 'http://api.geetest.com/gettype.php'
    headers = {
        'Host': 'api.geetest.com',
        'User-Agent': url_requests.random_userAgent(),
        'Referer': 'http://www.gsxt.gov.cn/index.html'
    }
    params = {
        'gt': gt,
        'callback': 'geetest_' + str(int(time.time() * 1000))
    }
    response = url_requests.get(url=url,
                                params=params,
                                headers=headers,
                                proxies=proxies)
    res = json.loads(response.content.split('(')[1][:-1])
    data = res.get('data', {})
    path = data.get('path', '/static/js/geetest.5.7.0.js')

    return path

def get_four(gt, challenge, path):
    """更新gt和challenge，同时获取被剪掉的滑快和完整图的图片地址，组合成字典返回"""

    url = 'http://api.geetest.com/get.php'
    headers = {
        'Host': 'api.geetest.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': url_requests.random_userAgent(),
        'Referer': 'http://www.gsxt.gov.cn/index.html'
    }
    params = {
        'gt': gt,
        'challenge': challenge,
        'product': 'popup',
        'offline': 'false',
        'protocol': '',
        'type': 'slide',
        'path': path,
        'callback': 'geetest_%s' % str(int(time.time() * 1000))
    }

    response = url_requests.get(url=url, params=params,
                                headers=headers, proxies=proxies)

    json_content = response.content.split('(')[1][:-1]
    data = json.loads(json_content)

    query_string = {}
    query_string['gt'] = data.get('gt')
    query_string['challenge'] = data.get('challenge')
    query_string['gb'] = data.get('bg')
    query_string['fullbg'] = data.get('fullbg')

    return query_string

def get_img(img_url):
    """传入图片地址，返回图片的二进制字节形式"""

    url = 'http://static.geetest.com/' + img_url

    response = url_requests.get(url=url, proxies=proxies)

    img_bytes = BytesIO(response.content)

    # img = Image.open(img_bytes)
    # img.show()
    return img_bytes

def get_geeTest(geeTest_params):
    """返回极验验证的三个验证参数"""

    url = 'http://api.geetest.com/ajax.php'
    headers = {
        'Host': 'api.geetest.com',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': url_requests.random_userAgent(),
        'Referer': 'http://www.gsxt.gov.cn/index.html'
    }
    if not geeTest_params:
        return None
    response = url_requests.get(url=url,
                                params=geeTest_params,
                                headers=headers,
                                proxies=proxies)

    json_string = response.content.split('(')[1][:-1]
    data = json.loads(json_string)
    if data['message'] != 'success':
        return None
    geeTest = {}
    geeTest['geetest_validate'] = data.get('validate')
    geeTest['geetest_seccode'] = data.get('validate') + '|jordan'

    return geeTest

def get_result(name, geeTest):
    """传入企业名称及极验验证通过的参数返回企业列表"""

    url = 'http://www.gsxt.gov.cn/corp-query-search-1.html'
    headers = {
        'Host': 'www.gsxt.gov.cn',
        'Origin': 'http://www.gsxt.gov.cn',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': url_requests.random_userAgent(),
        'Referer': 'http://www.gsxt.gov.cn/index.html'
    }
    geeTest.update({
        'searchword': name,
        'tab': 'ent_tab',
        'token': '49092658'     # 伪装验证码
    })

    response = url_requests.post(url=url, data=geeTest,
                                 headers=headers, proxies=proxies)

    soup = BeautifulSoup(response.content, 'lxml')

    result_count = soup.find('span', class_='search_result_span1')
    if int(result_count.text) == 0:
        print '未查询到相关企业'
        return []
    search_list = soup.find_all('a', class_='search_list_item db')
    result_items = []
    for each_search in search_list:
        search_name = each_search.find('h1', class_='f20')
        search_name = search_name.text.replace('\n', '')\
                                      .replace('\r', '')\
                                      .replace('\t', '')\
                                      .strip()
        detail_link = 'http://www.gsxt.gov.cn' + each_search['href']
        item = {}
        item['company'] = search_name
        item['detail'] = detail_link

        result_items.append(item)

    return result_items

def main(**kwargs):
    name = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')

    gt, challenge = get_gt_challenge()

    path = get_path(gt=gt)

    query_string = get_four(gt=gt, challenge=challenge, path=path)

    gt = query_string.get('gt')
    challenge = query_string.get('challenge')

    # bg_img = get_img(img_url=query_string.get('gb'))    # 待雷力弄好后这里需要改

    # full_img = get_img(img_url=query_string.get('fullbg'))
    gb = query_string.get('gb')  # type string
    # 这个online函数来自滑快验证码的接口
    geeTest_params = get_validate_data_based_online(challenge=challenge,
                                                    gt=gt,
                                                    incomplete_img_url=gb)
    geeTest = get_geeTest(geeTest_params=geeTest_params)
    if not geeTest:
        raise CaptchaFailed("Captcha OCR failed.") # 当验证码识别失败时， 返回 None
    geeTest['geetest_challenge'] = challenge

    result_items = get_result(name=name, geeTest=geeTest)

    return result_items

# def start(**kwargs):
#     """分布式查询入口，kwargs必须包含键data。data包含company和company_city"""
#
#     search_tag = kwargs.get('data')
#     global proxies
#     proxies = kwargs.get('proxies')
#     # proxies = None    # 当不需要用到代理时，不注释此行。
#
#     company_city = search_tag.get('company_city')
#     company = search_tag.get('company')
#
#     # 查询入口
#     times = 1
#     while times < 10:
#         match_items, result_items = main(name=company)
#         if match_items == 'failed':
#             print 'Captcha failed'
#             times += 1
#             time.sleep(3)
#         else:
#             # 可精确匹配那个需要把company_city重新组装进去，非精确匹配那个不用
#             for each in match_items:
#                 each['company_city'] = company_city
#
#             return match_items, result_items
#
#     raise UfException('Captcha failed')



if __name__ == '__main__':

    data = {
        'company': '昆明骏骐商贸有限公司',
        'company_city': '广东省'
    }
    proxies = None

    result = main(name='昆明骏骐商贸有限公司', proxies=proxies)

    print result