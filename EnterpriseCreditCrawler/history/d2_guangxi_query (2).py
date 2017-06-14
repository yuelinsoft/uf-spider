# -*- coding:utf-8 -*-
"""
    @author: "kexh"
    @updater: "kexh"(2016.12.28)
        [图片验证方式更换成滑块验证方式]
"""

from __future__ import unicode_literals
import re
import sys
import json
import copy
import math
import time
import random
from PIL import Image
from bs4 import BeautifulSoup
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO, BytesIO
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.uf_exception import RequestError
from EnterpriseCreditCrawler.common.slide_check_code_recognition import get_validate_data_based_online

'''
【调试日志】
time：2017/01/05
cause：一路跑下来都是{u'message': u'forbidden', u'success': 0}，重跑和循环都是这样。
note-1：
    返回值里头cookies会不定时被更新，但是imgload每次跑的时候是一样的。
    另外，gt是所有都一样，3e，我已经设置了返回值有包含gt就更新了，返回值也确实都包含gt。
    应该是imgload的关系, get_validate_data_based_online函数里头目前把imgload写固定的80.
note-2：
    已经把imgload改成randint的，但是还是不行。
    打印其他传值试试看，可能是有什么地方传值没有处理好。
    geetest.com的cookies要改成用gt_cookies。get_php原来竟然是用了固定的cookies。
note-3：
    已经把需要改成用gt_cookies的地方改好了，但是还是不行。
    我觉得是不是得看看图片地址和图片了？调试了一下，发现每次拿的url都是不一样的。说明这一部分是正常的。
    get_php函数要重点看，这个是verify函数开始之前的函数里头，最有可能调试力度不够的。
    这个里头的payload 的callback有个地方要改成调时间戳的。
    get_register里头有个refer的时间戳要改成随机的。
note-4：
    话说这么多forbidden，是不是跟后面改用gt_cookies有关呢？
    gt_cookies的值被我处理成只有一个key，是不是应该得改成多个传进去?可是用fiddler测了好像不需要也是可以的。
note-5：
    while None in [self.fullbg_url, self.bg_url] and ttime > 0:的判断处理改掉，直接return好了，因为很少遇到啊。
    改掉之后cookies直接返回空字符。
    多个地方的时间戳改掉之后反而成功率更低，是否应该把时间戳去掉。
---------------------------
time: 2017/01/06
cause: 目前forbidden的问题还是没有得到解决，把这两天调试的结果再梳理一下。
note-1：
    看cookies一路下来都是什么鬼，包括gt_cookies。
    gt更新的设置应该没有影响；imgload更新的设置应该没有影响；
    图片没有影响；调成时间戳的：payload 的callback，get_register的refer。
---------------------------
time: 2017/01/07
cause: 目前forbidden的问题还是没有得到解决，今天决定从几个新的角度去观察整个流程。
note-1：
    跟被调成时间戳的没有关系，应该跟cookies和gt_cookies有关系：
    url_home，url_gettype_php这两个经常返回空cookies，只在第一次返回时有值，为什么它能判断出是不是第一次调用？
    由于只有第一次有返回值，然后我的处理里面是没有返回值那就调用__init__的默认值，导致后面的判断都是根据默认值来的，那当然判断不通过了，sad。已优化这一点。
    【核心问题】第一次判断为什么那么多次都是forbidden呢？以及为什么只在第一次有返回值呢？
note-2：
    决定用fiddler和代码交替打断点、承接请求整个流程试试看，不行的话再试试其他法子。大概需要两个小时。下午开始弄。
    在此之前，想先去搜搜关于web接口断点调试的一些套路，看看有没有其他法子可以用。--No，工具基本是这样了，调试策略自己来定。
---------------------------
time: 2017/01/09
cause: 删掉了对url_home，url_gettype_php的请求，cookies全都变成空，可以跑到get_result里头，然后会被返回一行的html。
note：要让自己的代码和思路慢慢能够面对动荡不安，兵荒马乱的调试与线上环境。
    [Plan A]——针对一行的html，预计不会引进新的问题，比如在更前的地方得到错误结果。
    把对url_home的请求放到get_result前。
    --根本没有机会调通，老是被封，现在连第一个方法get_register都返回不了正常结果了。orz...
    --得到的是一行的html，2次测试结果；另外跑的很多次里面，都没有能到success那里，forbidden。
    [Plan B]——针对一行的html，预计不会引进新的问题，但前提是cookies的传入传出要做好。
    假如上面的方法不行，把home放到开头试一下，嗯，没错，这是Plan B。
    [Plan C]——针对一行的html，以及更高的识别通过率。
    假如上面的方法都不行，那就先保留home测一下下面的：
    0. gov.cn和geetest都要打bpu，需要用到的脚本片段要先单独准备好。
    1. 前半部分用浏览器跑，然后到get_register打断点，用脚本跑
    2.A. 用浏览器跑滑块，滑到正确位置
    2.B. 用浏览器跑一下前面img url的获取，然后程序计算值
    3. slide_verify的url_requests用脚本跑，前提是在fiddler里打好bpu，把值给写过来。
    4. 然后把home删了测一下上面的1-3.
    [Plan D]——针对提高识别通过率。
    假如上面的方法终于实现可以简洁地返回正确的非一行html。那么提高识别通过率的话，需要从下面两种思路入手：
    （1）go方法：
    1.



'''

class SlideVerify():
    '''
    slide_verify use them:
        1. get_home
        2. get_php
        3. get_raw_img
    '''

    def __init__(self, cookies, gt_cookies):
        self.url_home = 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
        self.url_start_captcha = 'http://gx.gsxt.gov.cn/pc-geetest/register?t=' + str(int(time.time() * 1000))
        # self.url_gettype_php = 'http://api.geetest.com/gettype.php?callback=geetest_' + str(int(time.time() * 1000))
        self.url_get_php = 'http://api.geetest.com/get.php'
        self.url_ajax = 'http://api.geetest.com/ajax.php'
        self.fullbg_url = None
        self.bg_url = None

        self.challenge = None
        self.gt = None

        self.cookies = cookies
        self.gt_cookies = gt_cookies

    def get_home(self):
        '''
        可能会被更改值的参数：
        self.cookies
        '''
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            # 'Connection': 'keep-alive',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url=self.url_home, headers=headers, proxies=proxies)
        print "00:",resp.cookies
        if len(str(resp.cookies).split(" "))>5:
            print 'get'
            self.cookies = str(resp.cookies).split(" ")[5] + ";" + str(resp.cookies).split(" ")[1]
        elif 5>len(str(resp.cookies).split(" "))>2:
            print 'get2'
            self.cookies = self.cookies.split(";")[0] + ";" + str(resp.cookies).split(" ")[1]
        resp.close()

    def get_register(self):
        '''
        可能会被更改值的参数：
        self.cookies
        self.challenge(32bit)
        self.gt
        '''
        headers = {
            'Cookie':'',#self.cookies
            'Host': 'gx.gsxt.gov.cn',
            'Referer': 'http://sc.gsxt.gov.cn/ztxy.do?method=index&random=1483924925344' ,#+ str(int(time.time() * 1000)),
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        resp = url_requests.get(self.url_start_captcha, headers=headers, proxies=proxies)
        print 11, resp.cookies
# < RequestsCookieJar[ < Cookie JSESSIONID = yDcJY1kdRLNcQCGLxP4vL5XhLSc1jpvzJh4ZGp8sndsZjyLQ9QTQ!-1937398610 for gx.gsxt.gov.cn / >, < Cookie insert_cookie=72414398 for gx.gsxt.gov.cn / >] >

#<RequestsCookieJar[<Cookie JSESSIONID=hx0GY1sVD85vBGHkhvNbMnNbLpyCy8PsM25D5N1WGH8kpyLnqdXp!1439207493 for gx.gsxt.gov.cn/>, <Cookie insert_cookie=62339635 for gx.gsxt.gov.cn/>]>

        # if len(str(resp.cookies).split(" "))>1:
        #     self.cookies = self.cookies.split(";")[0] + ";" + str(resp.cookies).split(" ")[1]
        part_data = resp.json()
        if part_data['success'] == 1:
            self.challenge = part_data['challenge']
            self.gt = part_data['gt']
        resp.close()
        print 'self.challenge[30:]', self.challenge[30:]

    # def gettype_php(self):
    #     '''
    #     可能会被更改值的参数：
    #     self.gt_cookies
    #     '''
    #     headers = {
    #         'Host': 'api.geetest.com',
    #         'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml',
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    #     }
    #     resp = url_requests.get(self.url_gettype_php, headers=headers, proxies=proxies)
    #     print "01:",resp.cookies
    #     if len(str(resp.cookies).split(" "))>1:
    #         self.gt_cookies = str(resp.cookies).split(" ")[1].split(";")[0]
    #     resp.close()

    def get_php(self):
        '''
        可能会被更改值的参数：
        self.fullbg_url
        self.bg_url
        self.challenge(34bit)
        self.gt
        '''
        payload = {
            'gt': self.gt,
            'challenge': self.challenge,
            'product': 'popup',
            'offline': 'false',
            'type': 'slide',
            'callback': 'geetest_' + str(int(time.time() * 1000))
        }
        headers = {
            'Cookie': '',#self.gt_cookies + '; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2215899a7431eb8-0a7f9e6c6a7ccf-6a191178-2073600-15899a7431f3f1%22%7D; _ga=GA1.2.973165129.1481703301; _gat=1; Hm_lvt_25b04a5e7a64668b9b88e2711fb5f0c4=1481617879,1481703301,1481764705,1482283938; Hm_lpvt_25b04a5e7a64668b9b88e2711fb5f0c4=1482284742; _qddaz=QD.mitwlq.77c5re.ivx9jple',
            'Host': 'api.geetest.com',
            'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
        }
        r = url_requests.get(self.url_get_php, headers=headers, params=payload, proxies=proxies)
        gt = re.search('"gt": "(.*?)"', r.text)
        gt = gt.group(1) if gt else 'Unknown'
        # challenge = re.search('"challenge": "(.*?)"', r.text)
        challenge = re.search('"challenge": "(.*?)"', r.text)
        challenge = challenge.group(1) if challenge else 'Unknown'
        bg = re.search('"bg": "(.*?)"', r.text)
        bg = 'http://static.geetest.com/' + bg.group(1) if bg else 'Unknown'
        fullbg = re.search('"fullbg": "(.*?)"', r.text)
        fullbg = 'http://static.geetest.com/' + fullbg.group(1) if fullbg else 'Unknown'
        if 'Unknown' not in [challenge, fullbg, bg]:
            self.gt = gt
            self.challenge = challenge
            self.bg_url = bg
            self.fullbg_url = fullbg
        print 'self.challenge[30:]',self.challenge[30:]

    def get_raw_img(self):
        headers = {
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.71 Safari/537.36')
        }
        r_bg = url_requests.get(self.bg_url, headers = headers, proxies=proxies)
        r_fullbg = url_requests.get(self.fullbg_url, headers = headers, proxies=proxies)
        raw_chunk_img = BytesIO(r_bg.content)
        raw_source_img = BytesIO(r_fullbg.content)
        return raw_source_img, raw_chunk_img

    def slide_verify(self):
        '''
        计算 payload（gt, challenge, passtime, a, userresponse, imgload, callback），并进行请求。
        :return: geetest_1482834227425({"success": 1,"message":"success","validate":"87781b9224dc550f36956d39cb1c4806","score":1})
        '''
        print self.cookies
        print self.gt_cookies
        self.get_home()
        print self.cookies
        print self.gt_cookies
        self.get_register()
        # print self.cookies
        # print self.gt_cookies
        # self.gettype_php()
        # print self.cookies
        # print self.gt_cookies
        self.get_php()
        # print self.cookies
        # print self.gt_cookies
        if None in [self.fullbg_url, self.bg_url]:
            return self.cookies, self.gt_cookies, dict(success=0, message=''), None
        else:
            headers = {
            'Host': 'api.geetest.com',
            # 'Cookie': self.gt_cookies + '; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2215899a7431eb8-0a7f9e6c6a7ccf-6a191178-2073600-15899a7431f3f1%22%7D; _ga=GA1.2.973165129.1481703301; _gat=1; Hm_lvt_25b04a5e7a64668b9b88e2711fb5f0c4=1481617879,1481703301,1481764705,1482283938; Hm_lpvt_25b04a5e7a64668b9b88e2711fb5f0c4=1482284742; _qddaz=QD.mitwlq.77c5re.ivx9jple',
            'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.71 Safari/537.36')
            }
            raw_source_img, raw_chunk_img = self.get_raw_img()
            payload = get_validate_data_based_online(self.challenge, self.gt, raw_source_img, raw_chunk_img)

            response = url_requests.get(url = self.url_ajax, headers = headers, params=payload, proxies=proxies)
            slide_result_d = json.loads(response.content.split("(")[1][:-1])
            print slide_result_d
            print self.cookies
            print self.gt_cookies
            if slide_result_d.has_key('validate'):
                geetest_data = dict(geetest_challenge=self.challenge, geetest_validate=slide_result_d["validate"],geetest_seccode=slide_result_d["validate"] + '|jordan')
                return self.cookies, self.gt_cookies, slide_result_d, geetest_data
            else:
                return self.cookies, self.gt_cookies, dict(success=0, message=''), None

def verify(url_validate, cookies, geetest_data):
    '''
    主要传值包括：
    geetest_challenge=e3b4e19ab72c245c1c88105c7764dfc2ce
    geetest_validate=ff1b2581c0f9f26b7ced369386784ca2
    geetest_seccode=ff1b2581c0f9f26b7ced369386784ca2%7Cjordan
    :return: {"status":"success","version":"3.3.0"}
    '''
    headers = {
            'Host': 'gx.gsxt.gov.cn',
            'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml',
            'Cookie': cookies,
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
    resp = url_requests.post(url=url_validate,data=geetest_data,headers=headers,proxies=proxies)
    js = json.loads(resp.content)#.split("(")[1].split(")")[0])
    status = js.get('status')
    return status

# def get_home():
#     '''
#     可能会被更改值的参数：
#     self.cookies
#     '''
#     url_home = 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml'
#     headers = {
#         'Host': 'gx.gsxt.gov.cn',
#         # 'Connection': 'keep-alive',
#         # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#         'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
#                        'AppleWebKit/537.36 (KHTML, like Gecko) '
#                        'Chrome/54.0.2840.99 Safari/537.36')
#     }
#     cookies = ""
#     while len(str(cookies).split(" "))>5:
#         resp = url_requests.get(url=url_home, headers=headers, proxies=proxies)
#         cookies = resp.cookies
#         cookies = str(cookies).split(" ")[5] + ";" + str(cookies).split(" ")[1]
#         return cookies

def get_result(url_result, company, cookies, geetest_data):
    '''
    主要传值包括：
    params: urlflag, challenge
    data: urlflag, nowNum, keyword, clear
    :return: search result
    '''
    #   only need them:  'Host: gx.gsxt.gov.cn
    # User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36
    # Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
    # Referer: http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml
    # Cookie: JSESSIONID=hQBmYrkWfpL2lT4cG1HFwdJnTNjJ1bkQMHPXb95J34LH14SwGVZQ!1832446435; insert_cookie=48249391
    # Content-Length: 231
    # '
    headers = {
        'Host': 'gx.gsxt.gov.cn',
        'Origin': 'http://gx.gsxt.gov.cn',
        'Referer': 'http://gx.gsxt.gov.cn/sydq/loginSydqAction!sydq.dhtml',
        'Cookie': cookies,
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.99 Safari/537.36'),
        'Content-Length': '250',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    params = dict(urlflag=0, challenge=geetest_data["geetest_challenge"])
    data = dict(urlflag='', nowNum='', keyword=company, clear='true')
    print cookies
    # print dict(insert_cookie=cookies.split(";")[0].split("=")[1],JSESSIONID=cookies.split(";")[1].split("=")[1])
    # 这个log里面也有出现报错的，应该要加判断的
    # Cookie = dict(insert_cookie=cookies.split(";")[0].split("=")[1],JSESSIONID=cookies.split(";")[1].split("=")[1]) # ,cookies=Cookie
    resp = url_requests.post(url=url_result,params=params,data=data,headers=headers,proxies=proxies)

    html = resp.content
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
                print soup.select('div.contentA1 > p')[0].text
                return []

            links = soup.select('div.search-result > ul > li > h3')
            if not links:
                raise Exception('query failed, please try it again.')
            result_list = []
            for each_link in links:
                link = each_link['onclick'].split('"')[1]
                result_list.append(link)
            return result_list

def main(**kwargs):
    '''
    main use them:
        1. SlideVerify - slide_verify
        2. verify
        3. get_result
    '''
    company = kwargs.get('name')
    global proxies
    proxies = kwargs.get('proxies')
    _IP_POOL = [
        'http://120.76.164.186:2323',
        'http://120.76.138.208:2323',
        'http://120.76.130.17:2323',
        'http://120.76.245.35:2323',
    ]
    proxies = {
        'http': _IP_POOL[3],
        'https': _IP_POOL[3]
    }
    url_validate = 'http://www.gxqyxygs.gov.cn/pc-geetest/validate'
    url_result = 'http://www.gxqyxygs.gov.cn/es/esAction!entlist.dhtml'

    btime = 8
    cookies = None
    gt_cookies = None
    slide_result_d = dict(success=0, message='')
    geetest_data = {}
    while slide_result_d["success"] != 1 and slide_result_d["message"] != "success" and btime > 0:
        vf = SlideVerify(cookies, gt_cookies)
        cookies, gt_cookies, slide_result_d, geetest_data = vf.slide_verify()
        btime = btime - 1

    if slide_result_d["success"] != 1 and slide_result_d["message"] != "success":
        if slide_result_d["message"] == "fail":
            print '验证码失败'
            raise RequestError('captcha: fail')
        else:
            print '验证码未知错误'
            raise RequestError('captcha: unknown fail')
    else:
        status = verify(url_validate, cookies, geetest_data)
        if slide_result_d["message"] == "fail" or status == 'fail':
            print '验证码失败'
            raise RequestError('captcha: fail')
        elif status == 'success':
            print '验证码成功！'
            result_list = get_result(url_result, company, cookies, geetest_data)
            return result_list
        else:
            print '验证码未知错误'
            raise RequestError('captcha: unknown fail')

if __name__ == "__main__":
    # for i in range(50):
    print main(name='腾讯')
        # time.sleep(62)
        # print "%s %s %s" % ("*" * 20, 'next one', "*" * 20)