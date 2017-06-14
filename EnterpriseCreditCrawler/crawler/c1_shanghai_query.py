# -*- coding: utf-8 -*-

"""
    @author: "lijianbin"

    滑块上海
"""


from __future__ import  unicode_literals
import re
import json
import time
import random
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import RequestError
from EnterpriseCreditCrawler.common.slide_check_code_recognition import (
     get_validate_data_based_offline)

def get_token_cookies():
    """获取token和cookies参数"""

    url = 'http://sh.gsxt.gov.cn/notice/'

    headers = {
        'Host': 'sh.gsxt.gov.cn',
        'Referer': 'http://gsxt.saic.gov.cn/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.99 Safari/537.36')
    }

    resp = url_requests.get(url, headers=headers, proxies=proxies)

    if resp.status_code != 200:
        raise RequestError('404 Error')
    html = resp.content

    soup = BeautifulSoup(html, 'lxml')

    token = soup.find('input', {'name': 'session.token'})['value']

    return token, resp.cookies

def get_challenge(cookies):
    """根据cookies获取challenge值"""

    url = 'http://sh.gsxt.gov.cn/notice/pc-geetest/register'

    headers = {
        'Host': 'sh.gsxt.gov.cn',
        'Referer': 'http://sh.gsxt.gov.cn/notice/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.99 Safari/537.36')
    }

    # 13位的时间戳，防止两次查询时间戳一致导致验证码识别失败
    timestamp = int(time.time() * 1000) + random.randint(0, 100)

    params = {
        't': timestamp
    }
    resp = url_requests.get(url=url, params=params,
                            headers=headers, cookies=cookies, proxies=proxies)

    data = json.loads(resp.content)

    challenge = data.get('challenge')

    return challenge

def verify(cookies, geetest_data):
    """将验证码得到的结果三个参数进行验证"""

    url = 'http://sh.gsxt.gov.cn/notice/pc-geetest/validate'

    headers = {
            'Host': 'sh.gsxt.gov.cn',
            'Referer': 'http://sh.gsxt.gov.cn/notice/',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
    try:
        resp = url_requests.post(url=url,
                             data=geetest_data,
                             headers=headers,
                             cookies=cookies,
                             proxies=proxies)

        js = json.loads(resp.content)

        status = js.get('status')

        return status
    except:
        raise

def get_result(name, token, cookies, geetest_data):
    """组装所有参数，获取结果。"""

    url = 'http://sh.gsxt.gov.cn/notice/search/ent_info_list'
    headers = {
        'Host': 'sh.gsxt.gov.cn',
        'Referer': 'http://sh.gsxt.gov.cn/notice/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.99 Safari/537.36')
    }

    geetest_data['condition.searchType'] = 1
    geetest_data['captcha'] = ''
    geetest_data['session.token'] = token
    geetest_data['condition.keyword'] = name

    resp = url_requests.post(url=url,
                             data=geetest_data,
                             headers=headers,
                             cookies=cookies,
                             proxies=proxies)

    html = resp.content

    soup = BeautifulSoup(html, 'lxml')
    if not soup:
        raise RequestError('query failed, please try it again.')

    result_num = soup.select_one('div.contentA1 > p > span')

    if not result_num:
        raise RequestError('query failed, please try it again.')

    if int(result_num.text) == 0:
        print soup.select_one('div.contentA1 > p').text
        return []

    print soup.select_one('div.contentA1 > p').text
    links = soup.find_all('div', {'class': 'tableContent page-item'})
    if not links:
        raise RequestError('query failed, please try it again.')

    result_list = []
    for each_link in links:
        item = {}
        company = each_link.find('td', {'colspan':'6'}).text.strip()
        tag_i = each_link.i.string.strip()
        item['company'] = company.replace(tag_i, '').strip()
        item['detail'] = each_link['onclick'].split("'")[1]
        result_list.append(item)

    return result_list

def main(**kwargs):

    company = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')
    # 获取token和cookies
    token, cookies =get_token_cookies()

    # 获取challenge
    challenge = get_challenge(cookies)

    # 获取极验验证码参数， type： dict
    geetest_data = get_validate_data_based_offline(challenge=challenge)

    # 判断极验参数是否正确
    status = verify(cookies, geetest_data)
    if status == 'fail':
        print '验证码失败'.encode('utf-8')
        raise RequestError('captcha: fail')
    elif status == 'success':
        print '验证码成功！'.encode('utf-8')
        result_list = get_result(company, token, cookies, geetest_data)
        return result_list
    else:
        print status
        raise RequestError('captcha: unknown fail')

if __name__ == '__main__':

    print main(name='腾讯')


