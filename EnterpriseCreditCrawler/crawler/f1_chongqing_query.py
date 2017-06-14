# -*- coding:utf-8 -*-
"""
    create in 2016.12.27

    @author: lijianbin

"""

from __future__ import  unicode_literals
import json
import time
# import random
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
# from EnterpriseCreditCrawler.common.uf_exception import RequestError
from EnterpriseCreditCrawler.common.slide_check_code_recognition import (
    get_validate_data_based_offline)


def get_key():
    """获取headers里面需要的accept-key的值"""

    url = 'http://cq.gsxt.gov.cn/search/tags/s.t'
    headers = {
        'Host': 'cq.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://cq.gsxt.gov.cn/'
    }

    response = url_requests.get(url=url, headers=headers)

    soup = BeautifulSoup(response.content, 'lxml')

    key = soup.find('input', {'id':'s_tn_val'})['value']

    return key

def get_gt_challenge(key):
    """get gt and challenge"""

    url = 'http://cq.gsxt.gov.cn/caic/pub/geetest/auth'
    headers = {
        'Accept-key': key,
        'Host': 'cq.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://cq.gsxt.gov.cn/'
    }

    params = {
        't': int(time.time() * 1000)
    }

    response = url_requests.post(url=url,
                                 params=params,
                                 headers=headers,
                                 proxies=proxies)

    res = json.loads(response.content)

    gt = res.get('gt')
    challenge = res.get('challenge')

    return gt, challenge

def get_path(gt):
    """"""

    url = 'http://api.geetest.com/gettype.php'
    headers = {
        'Host': 'api.geetest.com',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://cq.gsxt.gov.cn/'
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

    path = res.get('path', '/static/js/geetest.5.7.0.js')

    return path, response.cookies

def get_realChallenge(gt, challenge, path, cookies):
    """get real challenge"""

    url = 'http://api.geetest.com/get.php'
    headers = {
        'Host': 'api.geetest.com',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://cq.gsxt.gov.cn/'
    }
    params = {
        'gt': gt,
        'challenge': challenge,
        'product': 'popup',
        'lang':	'zh-cn',
        'offline': 'false',
        'protocol': ''	,
        'type':	'slide',
        'path':	path, #'/static/js/geetest.5.7.0.js',
        'callback':	'geetest_' + str(int(time.time() * 1000))
    }

    response = url_requests.get(url=url,
                                params=params,
                                headers=headers,
                                cookies=cookies,
                                proxies=proxies)

    res = json.loads(response.content.split('(')[1][:-1])

    real_challenge = res.get('challenge')

    return real_challenge

def get_result(name, key, geeTest):
    """"""

    t = time.time()

    url = 'http://cq.gsxt.gov.cn/caic/pub/api/s'
    headers = {
        'Accept-key': key,
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'cq.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://cq.gsxt.gov.cn/'
    }
    params = {
        't': int(time.time() * 1000)
    }

    geeTest['t'] = str(int(time.time() * 1000))

    jsn = 'zsearch=%s' % str(json.dumps({"kd": "1",
                                     "pageIndex": "1",
                                     "t": str(int(time.time() * 1000)),
                                     "tn": geeTest,
                                     "wd": name
                                    }))

    response = url_requests.post(url=url,
                                 params=params,
                                 data=jsn,
                                 headers=headers,
                                 proxies=proxies)

    result = json.loads(response.content)

    results = result.get('rows')
    # 从结果中找出能精确匹配的那条，如果没有，则result返回[]
    result = []
    for each_row in results:     # each_row type:dict
        item = {}
        item['company'] = each_row['entnameHL'].strip()
        item['detail'] = each_row
        result.append(item)

    return result

def main(**kwargs):
    """"""

    company = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')

    # 获取关键key
    key = get_key()

    # 获取gt and challenge
    gt, challenge = get_gt_challenge(key=key)

    # 获取path
    path, cookies = get_path(gt=gt)

    # 获取真正的challenge参数
    challenge = get_realChallenge(gt=gt,
                                  challenge=challenge,
                                  path=path,
                                  cookies=cookies)

    # 获取滑快验证码极验参数，dict
    geeTest = get_validate_data_based_offline(challenge=challenge)

    # 获取搜索结果企业列表
    result = get_result(name=company,key=key, geeTest=geeTest)

    return result

if __name__ == '__main__':

    print main(name='璧山区香熹庄食品经营部')