# -*- coding:utf-8 -*-
"""
    @author: "kexh"
    @updater: "kexh"(2017.01.10)
        [图片验证方式更换成滑块验证方式]
"""

from __future__ import unicode_literals
import json
import time
from io import BytesIO
from PIL import Image
import random
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import (CaptchaFailed, RequestError)
from EnterpriseCreditCrawler.common.slide_check_code_recognition import (
     get_validate_data_based_online)
'''
更新日志：
2017/01/11：
get_fourParams 出现请求失败：
EnterpriseCreditCrawler.common.uf_exception.IpRefused: <Response [403]>: （禁止） 服务器拒绝请求。 
get_challenge里头传cookies给get_fourParams，之前是get_cookies的值直接用。
但是get_challenge里头的cookies经常是空的，所以老的cookies不会被改掉。
感觉改了之后还是经常出现403.
另外，把代理加上了。
2017/01/16：
before：问题跟上面类似。
after：'http://gx.gsxt.gov.cn/pc-geetest/register'这个的请求放到while里头，跑出来的结果很少403了，但是，forbidden很多。

'''
headers = {
        'Host': 'gx.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://gx.gsxt.gov.cn/guangxi'
    }

def get_cookies():

    url = 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
    headers = {
        'Host': 'gx.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://gx.gsxt.gov.cn/guangxi'
    }

    response = url_requests.get(url=url, headers=headers, proxies=proxies)
    # 有时会出现没有返回cookies的情况，不过再套一层循环不太好，所以对这种例外情况不做特殊处理。
    return response.cookies

def get_challenge(cookies):

    url = 'http://gx.gsxt.gov.cn/pc-geetest/register'

    params = {
        't': int(time.time() * 1000)
    }

    response = url_requests.get(url=url,
                                params=params,
                                cookies=cookies,
                                headers=headers,
                                proxies=proxies)

    cha = json.loads(response.content)
    # print response.cookies
    # print len(str(response).split(' '))
    if len(str(response.cookies).split(" "))>=5:
        cookies = response.cookies
    gt = cha.get('gt')
    challenge = cha.get('challenge')

    return cookies, gt, challenge

# def get_fourParams(gt, challenge, cookies):
#
#     url = 'http://api.geetest.com/get.php'
#     headers = {
#         'Host': 'api.geetest.com',
#         'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
#                        'AppleWebKit/537.36 (KHTML, like Gecko) '
#                        'Chrome/55.0.2883.87 Safari/537.36'),
#         'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
#     }
#     params = {
#         'gt': gt,
#         'challenge': challenge,
#         'product': 'popup',
#         # 'lang': 'zh-cn',#
#         'offline': 'false',
#         # 'protocol': '',#
#         'type': 'slide',
#         # 'path': '/static/js/geetest.5.7.0.js',#
#         'callback': 'geetest_' + str(int(time.time() * 1000))
#     }
#
#     response = url_requests.get(url=url,
#                                 params=params,
#                                 headers=headers,
#                                 cookies=cookies,
#                                 proxies=proxies)
#
#     res = json.loads(response.content.split('(')[1][:-1])
#     # print response.cookies
#     # print len(str(response).split(' '))
#     # if len(str(response.cookies).split(" ")) > 2:
#     #     cookies = response.cookies
#
#     # real_challenge = res.get('challenge')
#
#     return cookies, res

class FParams():
    def __init__(self, gt, challenge, cookies):
        self.gt = gt
        self.challenge = challenge
        self.cookies = cookies

    def get_fourParams(self):
        url = 'http://api.geetest.com/get.php'
        headers = {
            'Host': 'api.geetest.com',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/55.0.2883.87 Safari/537.36'),
            'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
        }
        params = {
            'gt': self.gt,
            'challenge': self.challenge,
            'product': 'popup',
            # 'lang': 'zh-cn',#
            'offline': 'false',
            # 'protocol': '',#
            'type': 'slide',
            # 'path': '/static/js/geetest.5.7.0.js',#
            'callback': 'geetest_' + str(int(time.time() * 1000))
        }

        response = url_requests.get(url=url,
                                    params=params,
                                    headers=headers,
                                    cookies=self.cookies,
                                    proxies=proxies)

        # print response.cookies
        # print len(str(response).split(' '))
        # if len(str(response.cookies).split(" ")) > 2:
        #     cookies = response.cookies

        res = json.loads(response.content.split('(')[1][:-1])
        self.challenge = res.get('challenge')if res.has_key('challenge') else 'Unknown'
        self.gt = res.get('gt')if res.has_key('gt') else self.gt
        # 不完整图
        bg_url = 'http://static.geetest.com/' + res.get('bg')if res.has_key('bg') else 'Unknown'
        # 完整图
        fullbg_url = 'http://static.geetest.com/' + res.get('fullbg')if  res.has_key('fullbg') else 'Unknown'

        return self.cookies, self.challenge, self.gt, bg_url, fullbg_url


def get_image(image_url):
    """获取验证码图片

    :param image_url: 验证码图片url地址
    :return: 验证码图片Image对象
    """

    response = url_requests.get(url=image_url, proxies=proxies)
    img = BytesIO(response.content)

    return img

# 获取validate
def get_validate(geeTest, cookies):
    """获取validate"""

    url = 'http://api.geetest.com/ajax.php'
    headers = {
        'Host': 'api.geetest.com',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
    }
    print('get_validate: ',time.ctime())
    response = url_requests.get(url=url,
                                params=geeTest,
                                cookies=cookies,
                                headers=headers,
                                proxies=proxies)
    # return None 的是为了方便重跑。
    try:
        gee = json.loads(response.content.split('(')[1][:-1])
        print(gee)
        if gee.has_key('validate'):
            validate = gee.get('validate')
            return validate
        elif gee.has_key('message'):
            if gee.get('message') == 'success':
                raise CaptchaFailed('success but not key [validate] here. its return is:'+str(gee))
            else:
                raise CaptchaFailed('not [success] here. its return is:'+str(gee))
        else:
            return None
    except:
        print("[log]get_validate's content is not json format.")
        return None

def varify_validate(geetest, cookies):

    url = 'http://gx.gsxt.gov.cn/pc-geetest/validate'

    response = url_requests.post(url=url,
                                 data=geetest,
                                 cookies=cookies,
                                 headers=headers,
                                 proxies=proxies)
    # print response.content
    return response.content

def get_result(name, challeng, cookies):

    url = 'http://gx.gsxt.gov.cn/es/esAction!entlist.dhtml'

    params = {
        'urlflag': 0,
        'challenge': challeng
    }
    data = {
        'nowNum':'',
        'keyword': name,
        'urlflag': 0,
        'clear': '请输入企业名称、统一社会信用代码或注册号'
    }

    response = url_requests.post(url=url,
                                 params=params,
                                 data=data,
                                 headers=headers,
                                 cookies=cookies,
                                 proxies=proxies)
    print('get_result: ',time.ctime())
    html = response.content
    soup = BeautifulSoup(html, 'lxml')
    if not soup:
        raise Exception('Query failed. Please try it again.')
    elif soup.find('p',{'class': 'p01'}) != None:#u'技术人员'in soup.find('p',{'class': 'p01'}):
        raise Exception('Too frequent. Please try it again.')
    else:
        if soup.find('div', {'class': 'search-result'}):
            result_num = soup.select('div.search-result > p > span')
            if len(result_num)==0:
                raise Exception('query failed, please try it again.')

            if int(result_num[0].text) == 0:
                # print soup.select('div.contentA1 > p')[0].text
                return []

            links = soup.select('div.search-result > ul > li > h3')
            if not links:
                raise Exception('query failed, please try it again.')
            result_list = []
            for each_link in links:
                item = {}
                item['company'] = each_link.find('span').text.strip()
                item['detail'] = each_link['onclick'].split('"')[1]
                result_list.append(item)
            return result_list


def main(**kwargs):
    print('main: ',time.ctime())
    name = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')
    # 广西暂时不使用代理
    proxies = None
    btime = 4
    validate = None
    cookies = get_cookies()
    print(cookies)
    while validate==None and btime > 0:
        btime = btime - 1

        cookies, gt, challenge = get_challenge(cookies=cookies)

        fp = FParams(gt=gt, challenge=challenge, cookies=cookies)
        cookies, challenge, gt, bg_url, fullbg_url = fp.get_fourParams()
        if 'Unknown' in [challenge, gt, bg_url, fullbg_url]:
            validate = None
            print(333)
            time.sleep(2)
            continue

        # bg_img = get_image(bg_url)
        # fullbg_img = get_image(fullbg_url)

        # 获取滑快验证码极验参数，dict
        geeTest = get_validate_data_based_online(challenge=challenge,
                                                 gt=gt,
                                                 incomplete_img_url=bg_url)
                                                 # raw_source_img=fullbg_img,
                                                 # raw_chunk_img=bg_img)

        validate = get_validate(geeTest=geeTest, cookies=cookies)
    if validate==None:
        print(geeTest, cookies)
        print('验证码识别不通过。')
        raise CaptchaFailed('not key [message] here. captcha 1 : fail or unknown fail')
    else:
        geeTest = {
            'geetest_challenge': challenge,
            'geetest_validate': validate,
            'geetest_seccode': validate + '|jordan'
        }
        varify = varify_validate(geetest=geeTest, cookies=cookies)
        if 'success' not in varify:
            print('验证失败.')
            raise RequestError('captcha 2 : fail or unknown fail')
        else:
            result = get_result(name, challenge, cookies)
            return result

if __name__ == "__main__":
    for i in range(50):
        print(main(name='腾讯'))
        time.sleep(62)
        print("%s %s %s" % ("*" * 20, 'next one', "*" * 20))
