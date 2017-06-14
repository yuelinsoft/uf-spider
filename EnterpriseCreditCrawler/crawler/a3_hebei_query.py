# -*- coding:utf-8 -*-
"""
    @author: lijianbin
"""

from __future__ import unicode_literals
import json
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import RequestError
from EnterpriseCreditCrawler.common.slide_check_code_recognition import (
     get_validate_data_based_offline)


def get_token_cookies():
    """获取token和cookies参数"""

    url = 'http://www.hebscztxyxx.gov.cn/notice/'

    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'Referer': 'http://gsxt.saic.gov.cn/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.99 Safari/537.36')
    }

    resp = url_requests.get(url, headers=headers)

    html = resp.content

    soup = BeautifulSoup(html, 'lxml')

    token = soup.find('input', {'name': 'session.token'})['value']
    # print dict(resp.cookies)
    return token, resp.cookies

def get_challenge(cookies):
    """根据cookies获取challenge值"""

    url = 'http://www.hebscztxyxx.gov.cn/notice/pc-geetest/register'

    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'Referer': 'http://www.hebscztxyxx.gov.cn/notice/',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.99 Safari/537.36')
    }

    resp = url_requests.get(url=url, headers=headers, cookies=cookies)

    data = json.loads(resp.content)

    challenge = data.get('challenge')
    # print challenge
    return challenge

def verify(cookies, geetest_data):
    """将验证码得到的结果三个参数进行验证"""

    url = 'http://www.hebscztxyxx.gov.cn/notice/pc-geetest/validate'
    headers = {
            'Host': 'www.hebscztxyxx.gov.cn',
            'Referer': 'http://www.hebscztxyxx.gov.cn/notice/',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }

    resp = url_requests.post(url=url,
                             data=geetest_data,
                             headers=headers,
                             cookies=cookies)
    try:
        js = json.loads(resp.content)

        status = js.get('status')

        return status
    except:
        return None

def get_result(name, token, cookies, geetest_data):
    """组装所有参数，获取结果。"""

    url = 'http://www.hebscztxyxx.gov.cn/notice/search/ent_info_list'
    headers = {
        'Host': 'www.hebscztxyxx.gov.cn',
        'Referer': 'http://www.hebscztxyxx.gov.cn/notice/',
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
                             cookies=cookies)

    html = resp.content

    soup = BeautifulSoup(html, 'lxml')
    if soup:
        links = soup.find_all('div', {'class': 'tableContent'})
        result_list = []
        if links:
            for each_link in links:
                item = {}
                company = each_link.find('td', {'colspan': '6'}).text.strip()
                tag_i = each_link.i.string.strip()
                item['company'] = company.replace(tag_i, '').strip()
                item['detail'] = each_link['onclick'].split("'")[1]
                result_list.append(item)

        return result_list

def main(**kwargs):

    company = kwargs.get('name')

    # 获取token和cookies
    token, cookies =get_token_cookies()

    # 获取challenge
    challenge = get_challenge(cookies)

    # 获取极验验证码参数， type： dict
    geetest_data = get_validate_data_based_offline(challenge=challenge)

    # 判断极验参数是否正确
    status = verify(cookies, geetest_data)
    if status == 'fail':
        print '验证码失败'
        raise RequestError('captcha: fail')
    elif status == 'success':
        print '验证码成功！'
        result_list = get_result(company, token, cookies, geetest_data)
        return result_list
    else:
        print '验证码未知错误'
        raise RequestError('captcha: unknown fail')


if __name__ == '__main__':

    main(name='毛泽东')