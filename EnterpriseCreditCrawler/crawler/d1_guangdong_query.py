# -*- coding: utf-8 -*-

"""
    @author: "lijianbin"

    Query Templates
    改成滑快后的广东，可兼容广州，不兼容深圳
"""


from __future__ import  unicode_literals
import json
import time
import random
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import RequestError
from EnterpriseCreditCrawler.common.slide_check_code_recognition import (
                                            get_validate_data_based_offline)


# 获取challenge参数
def get_challenge():
    """获取challenge参数

    :rtype str or None
    """

    url = 'http://gd.gsxt.gov.cn/aiccips//verify/start.html'

    headers = {
        'Host': 'gd.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://gd.gsxt.gov.cn/'
    }

    time.sleep(random.randint(0, 3))
    params = {
        't': int(time.time() * 1000)
    }

    response = url_requests.get(url=url,
                                params=params,
                                headers=headers,
                                proxies=proxies)
    jsn = json.loads(response.content)

    challenge = jsn.get('challenge')

    return challenge

# 获取textField参数
def get_textfield(name, geeTest_params):
    """获取textField参数"""

    url = 'http://gsxt.gdgs.gov.cn/aiccips/verify/sec.html'
    headers = {
        'Host': 'gd.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://gd.gsxt.gov.cn/'
    }
    data = {
        'textfield': name,
    }
    data.update(geeTest_params)

    response = url_requests.post(url=url,
                                 data=data,
                                 headers=headers,
                                 proxies=proxies)
    jsn = json.loads(response.content)

    textfield = jsn.get('textfield')

    return textfield

# 用textfield参数获取query结果
def get_result(textfield):
    """用textfield参数获取query结果"""

    url = 'http://gd.gsxt.gov.cn/aiccips/CheckEntContext/showCheck.html'
    headers = {
        'Host': 'gd.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://gd.gsxt.gov.cn/'
    }
    data = {
        'textfield': textfield,
        'type': 'nomal'
    }

    response = url_requests.post(url=url,
                                 data=data,
                                 headers=headers,
                                 proxies=proxies)
    soup = BeautifulSoup(response.content, 'lxml')

    items_soup = soup.find('div', class_='mianBodyStyle')
    if not items_soup:
        raise RequestError('query failed, please try it again.')
    # 由items下面的第一个div标签的text来判断是否有结果
    status = items_soup.find('div', class_='textStyle')
    if not status:
        raise RequestError('query failed, please try it again.')
    # 查询结果数量
    result_num = int(status.find('span').text)

    if result_num == 0:
        return []   # 查询成功无数据
    else:
        items = items_soup.find_all('div', class_='clickStyle')
        result_list = []
        for i, each_item in enumerate(items):
            item = {}
            name = each_item.find('span', class_='rsfont').text.strip()
            href = each_item.find('a')['href'].strip()
            if '..' in href:
                href = href.replace('..', 'http://gd.gsxt.gov.cn/aiccips')
            item['company'] = name
            item['detail'] = href.encode('utf-8')

            result_list.append(item)

        return result_list

def main(**kwargs):

    company = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')

    # 获取challenge参数
    challenge = get_challenge()

    # 获取geeTest参数
    geeTest_params = get_validate_data_based_offline(challenge=challenge)

    # 组合geeTest与查询关键字，获取textField参数
    textfield = get_textfield(company, geeTest_params)

    # 用textfield参数获取query结果
    result_list = get_result(textfield)

    return result_list

if __name__ == '__main__':
    main(name='腾讯')