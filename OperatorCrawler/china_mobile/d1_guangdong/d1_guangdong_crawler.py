# coding=utf-8
from copy import copy
import time
import json
import random
import re
import sys

# from lxml import etree
# from selenium import webdriver
# from selenium.common.exceptions import *
# from selenium.webdriver import DesiredCapabilities

from d1_guangdong_month import getMonthSeq
import d1_guangdong_table as config
from ...public import (
    Request,
    get_UserAgent,
    return_result,
    password_encryption_based_ras
)

_time_wait = 2
_time_usual = 100
_time_special = 200

# capabilities = DesiredCapabilities.PHANTOMJS.copy()
# capabilities["phantomjs.page.settings.loadImages"] = False
# # phantom_path = r'C:\driver\phantomjs-2.1.1-windows\bin\phantomjs.exe'
# phantom_path = r'/home/mao/phantomjs/bin/phantomjs'


class ChinaMobile_GD():
    """中国移动-广东爬虫"""

    def __init__(self, phone_attr):
        # param phone_attr: 手机归属信息
        self.__headers = {
            'Accept': '*/*',
            'User-Agent': get_UserAgent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
        }
        self.browser = None
        self.cookies = dict()  # cookies
        self.phone_attr = phone_attr  # 手机属性
        self.user_items = list()  # 用户信息
        self.call_items = list()  # 通话信息
        self.note_items = list()  # 短信信息
        self.refresh_num = 3  # 更新峰值

    # end

    # @staticmethod
    # def getCookies(cookies_seq):
    #     """ 将selenium获得的cookie序列转为字典
    #     :return: dict(key=value)
    #     """
    #     cookie_dict = dict()
    #     if cookies_seq:
    #         for cookie in cookies_seq:
    #             cookie_dict[cookie['name']] = cookie['value']
    #     return cookie_dict

    # end


    # @staticmethod
    # def timeSleep(min=1, max=3):
    #     # 设置中断
    #     if min <= max:
    #         return time.sleep(random.uniform(min, max))
    #     else:
    #         raise ValueError('param value error')

    # end

    # @staticmethod
    # def judgeByMatch(pattern, string):
    #     # 通过match内容来判断相关类型
    #     try:
    #         re.match(pattern, string).group(1)
    #     except (IndexError, AttributeError):
    #         return False
    #     else:
    #         return True

    # end

    def getCode(self):
        """获取验证码

        :return: 结果字典（成功2000或失败非2000），无需要保存的数据
        """
        # def openBrowser():
        #     url = 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml'
        #     # self.browser = webdriver.PhantomJS(r'C:\driver\phantomjs-2.1.1-windows\bin\phantomjs.exe')
        #     # self.browser = webdriver.Chrome(r'C:\driver\chromedriver.exe')
        #     self.browser = webdriver.Chrome(r'/usr/bin/chromedriver')
        #     self.browser.get(url)
        #     self.browser.implicitly_wait(_time_usual)  # open the login page
        #     self.timeSleep()
        #     return True
        #
        # def acquireCode():
        #     try:
        #         self.browser.switch_to.frame('iframe_login_pop')
        #     except NoSuchFrameException as frame_ex:
        #         print frame_ex
        #         sys.exit(0)
        #     user_name_element = self.browser.find_element_by_id('mobile')
        #     user_name_element.clear()
        #     user_name_element.send_keys(self.phone_attr['phone'])
        #     try:
        #         self.browser.find_element_by_id('btn_get_dpw').click()
        #     except ElementNotVisibleException as ex:
        #         if self.refresh_num > 0:
        #             self.refresh_num -= 1
        #             self.browser.refresh()
        #             return acquireCode()  # 调用自身
        #         else:
        #             raise Exception(u'对不起,获取手机动态码失败')
        #     else:
        #         self.browser.implicitly_wait(
        #             _time_usual)  # open the login page
        #         # 　动态密码已发送，10分钟内有效。
        #         self.timeSleep()
        #         try:
        #             tips = self.browser.find_element_by_xpath(
        #                 '//span[@class="text"]').text.strip().encode('utf-8')
        #             print [tips]
        #         except (NoSuchElementException, WebDriverException):
        #             sys.exit(0)
        #         else:
        #             print tips
        #             if self.judgeByMatch('(动态密码已发送)', tips):
        #                 print u'hi,动态验证码已经发送到手机:' + self.phone_attr['phone']
        #                 return 2000
        #
        #             elif self.judgeByMatch('(动态密码发送失败)', tips):
        #                 print  u'hi,动态验证码无法发送到手机:' + self.phone_attr['phone']
        #                 return 4000
        #             else:
        #                 print tips

        # # 逻辑
        # if openBrowser():
        #     return acquireCode()
        # else:
        #     raise WebDriverException(u'无法调用驱动')
        def verification_code_trigger():
            """触发短信验证码发送的网络请求

            :return: Requests 类
            """
            form = {'mobile': self.phone_attr['phone']}
            url = 'https://gd.ac.10086.cn/ucs/ucs/getSmsCode.jsps'
            self.__headers['Referer'] = ('https://gd.ac.10086.cn/ucs/ucs/webPo'
                                         'pupLogin.jsps?reqType=0&channel=0&ci'
                                         'd=501143&area=%2Fcommodity&resource='
                                         '%2Fcommodity%2Fservicio%2Fnostandard'
                                         'serv%2FrealtimeListSearch%2Findex.js'
                                         'ps&loginType=3&optional=false&exp=&b'
                                         'ackURL=http%3A%2F%2Fgd.10086.cn%2Fmy'
                                         '%2FREALTIME_LIST_SEARCH.shtml')
            self.__headers['Host'] = ('gd.ac.10086.cn')
            self.__headers['Origin'] = ('https://gd.ac.10086.cn')
            self.__headers['X-Requested-With'] = ('XMLHttpRequest')
            options = {'method': 'post', 'url': url, 'form': form,
                       'timeout': 30, 'headers': self.__headers}
            response = Request.basic(options)
            return response if response else False

        def trigger_status():
            """对短信验证码网络请求进行逻辑判断

            :return: 结果字典（成功2000或失败非2000），无需要保存的数据
            """
            response = verification_code_trigger()
            if response:
                if response.status_code == 200:
                    try:
                        info = response.json()
                    except Exception as _:
                        return return_result(4100, [], desc=response.text)
                    if 'returnCode' in info and info['returnCode'] == '1000':
                        msg = info['failMsg']
                        return return_result(2000, [], desc=u'动态验证码请求: {}'
                                             .format(msg))
                    else:
                        # if 'failMessage' in info['content']:
                        #     msg = info['content']['failMessage']
                        # elif 'message' in info['content'][0]:
                        #     msg = info['content'][0]['message']
                        # else:
                        #     msg = info['content'][0]
                        msg = info
                        return return_result(5500, [], desc=u'动态验证码请求: {}'
                                             .format(msg))
                else:
                    return return_result(4000, [],
                                         desc=u'动态验证码请求: {}'
                                         .format(response.status_code))
            else:
                return return_result(4000, [], desc=u'动态验证码请求网络错误')

        return trigger_status()

    # def

    # def login(self):
    #     user_name_element = self.browser.find_element_by_id('mobile')  # 用户名框
    #     password_element = self.browser.find_element_by_name('password')  # 密码框
    #     dynamic_pw_element = self.browser.find_element_by_name(
    #         'dynamicCaptcha')  # 动态密码框
    #     login_element = self.browser.find_element_by_id('loginSubmit')  # 登录按钮
    #
    #     user_name_element.clear()
    #     user_name_element.send_keys(self.phone_attr['phone'])
    #
    #     password_element.clear()
    #     password_element.send_keys(self.phone_attr['password'])
    #
    #     dynamic_pw_element.send_keys(self.phone_attr['phone_pwd'])
    #     login_element.click()  # login after click
    #     self.browser.implicitly_wait(_time_special)
    #     return self.judgeLogin()  # 登陆态判断
    #
    # # def
    #
    # def judgeLogin(self):
    #     """ 进行登录判断
    #     :return:
    #     """
    #     try:
    #         tips = self.browser.find_element_by_xpath(
    #             '//span[@class="text"]').text.strip().encode('utf-8')
    #     except (NoSuchElementException, WebDriverException):
    #         return 2000
    #     else:
    #         print type(tips), len(tips)
    #         if self.judgeByMatch('(密码)', tips):
    #             print 'pw error'
    #             return 4600  # 密码错误
    #         elif self.judgeByMatch('(动态密码错误)', tips):
    #             return 4610  # 动态码错误
    #         elif tips == '':
    #             return 2000
    #         else:
    #             raise Exception(u'未知错误')

    # def

    def fetch_home_cookie(self):
        """获取 cookie 网络请求

        :return: Requests 类
        """
        form = {}
        url = 'http://gd.10086.cn/commodity/servicio/myService/queryBrand.jsps'
        self.__headers['Referer'] = ('http://gd.10086.cn/my/REALTIME_LIST_SEAR'
                                     'CH.shtml')
        self.__headers['Host'] = 'gd.ac.10086.cn'
        self.__headers['Origin'] = 'https://gd.ac.10086.cn'
        self.__headers['X-Requested-With'] = ('XMLHttpRequest')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers, 'cookies': self.cookies}
        response = Request.basic(options)
        return response if response else False

    def set_login_cookie(self):
        """对得到的 cookie 请求进行逻辑判断

        :return: 结果字典
        """
        from requests import utils, cookies

        home_cookie_response = self.fetch_home_cookie()
        if home_cookie_response:
            if home_cookie_response.status_code == 200:
                try:
                    # Path 不同,同样的 key 也会同时存在,因此采用字典去重
                    temp_cookie = utils.dict_from_cookiejar(self.cookies)
                    load_cookie = utils.dict_from_cookiejar(
                        home_cookie_response.cookies)
                    temp_cookie.update(load_cookie)
                    self.cookies = cookies.cookiejar_from_dict(temp_cookie)
                    content = home_cookie_response.json()['content']
                    return return_result(2000, [content],
                                         desc=u'获取主页 cookie 成功')
                except Exception as _:
                    return return_result(4100, [], desc=u'主页 cookie 不存在')
            else:
                return_result(4000, [], desc=u'获取主页 cookie 网络错误: {}'
                              .format(home_cookie_response.status_code))
        else:
            return return_result(4000, [], desc=u'获取主页 cookie 网络错误')

    def login_request(self, referer_url):
        """登陆网络请求

        :param referer_url: 相应的请求参数
        :return: Requests 类
        """
        form = {'mobile': self.phone_attr['phone_num'],
                'serPwd': '',
                'smsPwd': self.phone_attr['phone_pwd'],
                'imagCaptcha': '',
                'loginType': '1',
                'cookieMobile': '',
                'backURL': 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml'
                }
        url = 'https://gd.ac.10086.cn/ucs/ucs/webForm.jsps'
        self.__headers['Referer'] = referer_url
        self.__headers['Host'] = 'gd.ac.10086.cn'
        self.__headers['Origin'] = 'https://gd.ac.10086.cn'
        self.__headers['X-Requested-With'] = ('XMLHttpRequest')
        options = {'method': 'post', 'url': url, 'form': form,
                   'cookies': self.cookies, 'timeout': 30,
                   'headers': self.__headers}
        response = Request.basic(options)
        return response if response else False

    def login_handle(self, referer_url):
        """对登陆请求进行逻辑判断

        :param referer_url: 相应的请求参数
        :return: 结果字典
        """
        from requests import cookies

        login_response = self.login_request(referer_url[0])
        if login_response:
            if login_response.status_code == 200:
                try:
                    info = login_response.json()
                    msg = info['failMsg']
                except Exception as _:
                    return return_result(4100, [], desc=login_response.text)
                if 'returnCode' in info:
                    if info['returnCode'] == '1000':
                        self.cookies = cookies.merge_cookies(self.cookies,
                                                             login_response
                                                             .cookies)
                        return return_result(2000, [], desc=u'登陆请求: {}'
                                             .format(msg))
                    elif info['returnCode'] == '9080010007':
                        return return_result(4610, [], desc=u'登陆请求: {}'
                                             .format(msg))
                    else:
                        return return_result(4000, [info], desc=u'登陆请求: {}'
                                             .format(msg))
                else:
                    msg = info
                    return return_result(5500, [], desc=msg)
            else:
                return return_result(4000, [],
                                     desc=u'登陆请求: {}'
                                     .format(login_response.status_code))
        else:
            return return_result(4000, [], desc=u'登陆请求网络错误')

    def log_in(self):
        """登陆的逻辑判断

        :return: 结果字典
        """
        login_cookie_result = self.set_login_cookie()
        if login_cookie_result['code'] == 2000:
            return self.login_handle(login_cookie_result['data'])
        else:
            return login_cookie_result


    def online_request(self):
        """请求服务器（类似记录cookie）的网络请求

        :return: Requests 类
        """
        form = {}
        url = 'http://gd.10086.cn/common/include/public/isOnline.jsp'
        self.__headers['Referer'] = ('http://gd.10086.cn/my/REALTIME_LIST_SEAR'
                                     'CH.shtml')
        self.__headers['Host'] = ('gd.10086.cn')
        self.__headers['Origin'] = ('http://gd.10086.cn')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers, 'cookies': self.cookies}
        response = Request.basic(options)
        return response if response else False

    def set_online(self):
        """对请求服务器进行逻辑判断

        :return: 结果字典
        """
        from requests import cookies, utils

        online_response = self.online_request()
        if online_response:
            if online_response.status_code == 200:
                try:
                    temp_cookie = utils.dict_from_cookiejar(self.cookies)
                    load_cookie = utils.dict_from_cookiejar(online_response
                                                            .cookies)
                    temp_cookie.update(load_cookie)
                    self.cookies = cookies.cookiejar_from_dict(temp_cookie)
                    return return_result(2000, [], desc=u'获取 session 成功')
                except:
                    return return_result(4100, [], desc=u'获取 session 解析错误')
            else:
                return_result(4000, [], desc=u'获取 session 网络错误: {}'
                              .format(online_response.status_code))
        else:
            return return_result(4000, [], desc=u'获取 session 网络错误')

    def fetch_token(self):
        """获取 cookie 的网络请求

        :return: Requests 类
        """
        form = {
            'servCode': 'REALTIME_LIST_SEARCH',
            'operaType': 'QUERY',
            'Payment_startDate': '20170419000000',
            'Payment_endDate': '20170419235959',
        }
        url = ('http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeL'
               'istSearch/index.jsps')
        self.__headers['Referer'] = ('http://gd.10086.cn/my/REALTIME_LIST_SEAR'
                                     'CH.shtml')
        self.__headers['Host'] = ('gd.10086.cn')
        self.__headers['Origin'] = ('http://gd.10086.cn')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers, 'cookies': self.cookies}
        response = Request.basic(options)
        return response if response else False

    def set_token(self):
        """对 cookie 请求进行逻辑判断

        :return: 结果字典
        """
        from requests import cookies

        token_response = self.fetch_token()
        if token_response:
            if token_response.status_code == 200:
                try:
                    info = token_response.json()
                except:
                    return return_result(4000, [token_response.text],
                                         desc=u'获取 token 网络错误')
                if 'error.unauthorized' in token_response.text:
                    self.cookies = cookies.merge_cookies(self.cookies,
                                                         token_response.cookies)
                    return return_result(2000, [info], desc=u'获取 token 成功')
                else:
                    return return_result(5500, [token_response.text],
                                         desc=u'获取 token 网络错误')
            else:
                return return_result(4000, [], desc=u'获取 token : {}'
                                     .format(token_response.status_code))
        else:
            return return_result(4000, [], desc=u'获取 token 网络错误')

    def param_dict_parse(self, referer_url):
        """解析参数逻辑判断

        :param referer_url: 相应的请求参数
        :return: 结果字典
        """
        from requests import utils

        try:
            referer_url = referer_url[0]['content']
            param_dict = dict(referer_url=referer_url)
            cookies_dict = utils.dict_from_cookiejar(self.cookies)
            temp_sign = re.search(u'sign=(.*?)\&', referer_url)
            param_dict.update(st=cookies_dict['_st'],
                              token=cookies_dict['token'],
                              appid=cookies_dict['appId'],
                              sign=temp_sign.group(1)
                              )
            return return_result(2000, [param_dict], desc=u'param 解析成功')
        except:
            return return_result(4100, [referer_url], desc=u'param 解析错误')


    def auth_login_request(self, param_dict):
        """登陆认证网络请求

        :param param_dict: 相关请求参数字典
        :return: Requests 类
        """
        form = {'mobile': self.phone_attr['phone_num'],
                'serPwd': self.phone_attr['password'],
                'saType': '2',
                'channel': 'bsacNB',
                'st': param_dict['st'],
                'sign': param_dict['sign'],
                'token': param_dict['token'],
                'appid': param_dict['appid'],
                'backURL':'http://gd.10086.cn/ my/REALTIME_LIST_SEARCH.shtml',
                }
        url = 'https://gd.ac.10086.cn/ucs/ucs/secondAuth.jsps'
        self.__headers['Referer'] = param_dict['referer_url']
        self.__headers['Host'] = ('gd.10086.cn')
        self.__headers['Origin'] = ('http://gd.10086.cn')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers, 'cookies': self.cookies}
        response = Request.basic(options)
        return response if response else False

    def auth_login_handle(self, param_dict):
        """登陆认证网络请求

        :param param_dict: 相关请求参数字典
        :return: 结果字典
        """
        from requests import cookies, utils

        auth_login_response = self.auth_login_request(param_dict[0])
        if auth_login_response:
            if auth_login_response.status_code == 200:
                try:
                    temp_cookie = utils.dict_from_cookiejar(self.cookies)
                    load_cookie = utils.dict_from_cookiejar(auth_login_response
                                                            .cookies)
                    temp_cookie.update(load_cookie)
                    self.cookies = cookies.cookiejar_from_dict(temp_cookie)
                    info = auth_login_response.json()
                    msg = info['failMsg']
                    if info['returnCode'] == '1000':
                        return return_result(2000, [], desc=u'二次鉴权成功: {}'
                                             .format(msg))
                    elif info['returnCode'] == '0337004003':
                        return return_result(4600, [], desc=u'二次鉴权: {}'
                                             .format(msg))
                    else:
                        return return_result(5500, [info],
                                             desc=u'二次鉴权网络错误')
                except:
                    return return_result(4100, [auth_login_response.text],
                                         desc=u'二次鉴权解析错误')
            else:
                return_result(4000, [], desc=u'二次鉴权网络错误: {}'
                              .format(auth_login_response.status_code))
        else:
            return return_result(4000, [], desc=u'二次鉴权网络错误')

    def auth_log_in(self):
        """登陆逻辑总判断，包含登陆时候需要 hook 哪些 cookie 等必须的操作

        :return: 结果字典
        """
        online_result = self.set_online()
        if online_result['code'] == 2000:
            token_result = self.set_token()
            if token_result['code'] == 2000:
                param_dict = self.param_dict_parse(token_result['data'])
                if param_dict['code'] == 2000:
                    return self.auth_login_handle(param_dict['data'])
                else:
                    return param_dict
            else:
                return token_result
        else:
            return online_result

    def fetch_cookie(self):
        """对登陆逻辑的总判断进行封装

        :return: 结果字典
        """
        login_result = self.log_in()
        if login_result['code'] == 2000:
            return self.auth_log_in()
        else:
            return login_result


    def clawAllInfo(self):
        """信息爬取

        :return: 结果字典
        """
        # try:
        #     self.browser.find_element_by_xpath('//div[@id="mathBox"]/div/a[1]').click()  # 点击查询
        #     self.browser.implicitly_wait(_time_usual)
        # except NoSuchElementException as ex:
        #     return 4000
        # self.timeSleep()
        # self.cookies = self.getCookies(self.browser.get_cookies())     # cookies更新
        # if len(self.cookies) > 0:

        if self.cookies != dict():
            # self.clawUserInfo()  # 爬取用户信息
            # self.clawCallInfo()  # 爬取通话记录
            user_info = self.clawUserInfo()  # 爬取用户信息
            if user_info['code'] == 2000:
                call_info = self.clawCallInfo()  # 爬取通话记录
                return call_info
            else:
                return user_info
        else:
            return return_result(4000, [], desc=u'网络错误，cookie 为空')

    # end

    def clawUserInfo(self):
        """Get the basic information of the user
        :return:False/list
        """

        def queryInfo():
            """登陆验证逻辑判断，是否可以进行信息爬取

            :return: 结果字典
            """
            form = {'servCode': 'MY_BASICINFO'}
            url = 'http://gd.10086.cn/commodity/servicio/track/servicioDcstrack/query.jsps'
            self.__headers[
                'Referer'] = 'http://gd.10086.cn/my/myService/myBasicInfo.shtml'
            options = {'method': 'post', 'url': url, 'form': form,
                       'cookies': self.cookies, 'headers': self.__headers}
            response = Request.basic(options)
            if response:
                info = json.loads(response.text)
                if u'content' in info:
                    if u'COOKIE_USER_NUM' not in info['content']:
                        print u'未成功登陆'
                        return return_result(4000, [],
                                             desc=u'queryInfo 未成功登陆')
                    else:
                        print u'登录成功'
                        return getInfo()
                else:
                    print u'未成功登陆'
                    return return_result(4000, [], desc=u'queryInfo 未成功登陆')
            else:
                # return False
                return return_result(4000, [], desc=u'queryInfo 网络错误')

        # def

        def getInfo():
            """用户信息爬取

            :return: 结果字典
            """
            form = {'servCode': 'MY_BASICINFO',
                    'operaType': 'QUERY'
                    }
            url = ('http://gd.10086.cn/commodity/servicio/nostandardserv/mobil'
                   'eInfoQuery/index.jsps')
            self.__headers['Referer'] = ('http://gd.10086.cn/my/myService/myBa'
                                         'sicInfo.shtml')
            self.__headers['Host'] = 'gd.10086.cn'
            self.__headers['Origin'] = 'http://gd.10086.cn'
            options = {'method': 'post', 'url': url, 'form': form,
                       'cookies': self.cookies, 'timeout': 30,
                       'headers': self.__headers}
            response = Request.basic(options)
            if response:
                # return clawInfo(response.text)
                return clawInfo(response.content.decode('utf-8'))
            else:
                # return False
                return return_result(4000, [], desc=u'getInfo 网络错误')

        # def

        def clawInfo(text):
            """用户信息解析

            :param text: 用户信息 html 网页
            :return: 结果字典
            """
            try:
                # selector = etree.HTML(text)
                # table = selector.xpath('//table[@class="tb02"]')[0]
                # values =  table.xpath('tbody/tr[2]/td/text()')
                # if len(values) == 0:
                #     values =  table.xpath('tr[2]/td/text()')
                item = dict(
                    # phone = values[0],
                    # name = values[1],
                    # cert_num = values[2],
                    # open_date = values[4],
                    # uese_valid = re.search(u'用户状态</td>\\s+<td>(.*?)</td>',
                    #                        text),
                    user_valid=1,
                    company=self.phone_attr['company'],
                    province=self.phone_attr['province'],
                    city=self.phone_attr['city'],
                    # level=re.search(
                    #     u'STAR_LEVEL\.shtml" class="link">(.*?)</a>',
                    #     text).group(1),
                    # level=re.search(u'星级得分</td>\\s+<td>(.*?)</td>',
                    #                 text).group(1),
                    level=re.search(r"link'\)\.html\('(.*?)'\)", text).group(1),
                    phone=re.search(u'手机号码</td>\\s+<td>(.*?)</td>',
                                    text).group(1),
                    name=re.search(u'用户名</td>\\s+<td>(.*?)</td>',
                                   text).group(1),
                    cert_num=re.search(u'身份证</td>\\s+<td>(.*?)</td>',
                                       text).group(1),
                    open_date=re.search(u'入网时间</td>\\s+<td>(.*?)</td>',
                                        text).group(1),
                    product_name=re.search(u'所属品牌</td>\\s+<td>(.*?)</td>',
                                           text).group(1),
                    cert_type=u'身份证',
                    # province=self.phone_attr['province'],
                    # city=self.phone_attr['city'],
                )
                # 填充字段
                [item.setdefault(i, '') for i in config.COLUMN_USER]
                self.user_items.append(item)  # 保存记录
                return return_result(2000, [], desc=u'获取客户信息成功')
            except AttributeError as e:
                print(u'用户状态:{}', e.message)
                return return_result(4100, [text], desc=u'获取客户信息解析错误')
            except (IndexError, Exception) as e:
                # return False
                print(u'用户状态:{}', e.message)
                return return_result(4000, [text], desc=u'获取客户信息网络错误')

        # def
        return getInfo()

    # end

    def clawCallInfo(self):
        """通话记录以及短信记录信息解析

        :return: 结果字典
        """
        # """ Save all call records
        # :return: null
        # """
        item = {
            'cert_num': self.user_items[0]['cert_num'],
            'phone': self.user_items[0]['phone']
        }
        text_seq = self.getFiveMonthCall()
        # TODO: 不再需要判断字典类型,转而判断每个 text 的类型
        if isinstance(text_seq, dict):
            return text_seq
        # if len(text_seq) > 0:
        desc_list = [u'爬取记录成功，但存在未能爬取信息的月份：']
        for text in text_seq:
            if isinstance(text[1], dict):
                print(u'获取{}失败'.format(unicode(text[0])))
                desc_list.append(u'{}, 错误原因: {};'
                                 .format(unicode(text[0]),
                                         unicode(text[1]['desc'])))
            else:
                try:
                    results = json.loads(text[1])['content'][
                        'realtimeListSearchRspBean']['calldetail'][
                        'calldetaillist']
                    sms_results = (json.loads(text[1])['content'][
                                       'realtimeListSearchRspBean'][
                                       'smsdetail']['smsdetaillist'])
                except Exception as e:
                    print(u'获取{}失败'.format(unicode(text[0])))
                    print(e.message)
                    desc_list.append(u'{}, 错误原因: {};'
                                     .format(unicode(text[0]),
                                             unicode(text[1])))
                    continue
                for record in results:
                    temp = copy(item)
                    # 'place', 'time', 'time', 'chargefee','period', 'contnum', 'becall', 'conttype'
                    for k, v in record.items():
                        if k in config.KEY_CONVERT_CALL.keys():
                            column_name = config.KEY_CONVERT_CALL[k]
                            temp[column_name] = v
                    try:
                        # 入库修正
                        self.convertValues(temp)
                    except Exception as ex:
                        print(u'call 入库修正错误')
                        print(ex.message)
                        # for k, v in temp.items():
                        #     print k, v
                    self.call_items.append(temp)
                for record in sms_results:
                    temp = copy(item)
                    # 'time', 'fee', 'smstype', 'smsnum'
                    for k, v in record.items():
                        if k in config.KEY_CONVERT_NOTE_MOBILE.keys():
                            column_name = config.KEY_CONVERT_NOTE_MOBILE[k]
                            temp[column_name] = v
                    try:
                        # 入库修正
                        self.convert_value_note(temp)
                    except Exception as ex:
                        print(u'note 入库修正错误')
                        print(ex.message)
                        # for k, v in temp.items():
                        #     print k, v
                    self.note_items.append(temp)
        if len(desc_list) == 7:
            return return_result(2100, [''.join(desc_list)],
                                 desc=u'爬取内容网络错误')
        elif 7 > len(desc_list) > 1:
            return return_result(2001, [], desc=''.join(desc_list))
        elif len(desc_list) == 1:
            return return_result(2000, [], desc=u'爬取内容成功')
            # else:
            #     print 'call records not found'

    # end


    def convertValues(self, temp):
        """通话记录信息字典 key 转换成统一类型

        :param temp: 需要转换的信息字典
        :return: 转换后的信息字典
        """
        key = temp.keys()
        if 'call_type' in key:
            call_type = {u'主叫': 1, u'被叫': 2}
            if temp['call_type'] in call_type.keys():
                temp['call_type'] = call_type[temp['call_type']]
            else:
                temp['call_type'] = 3

        if 'land_type' in key:
            land_type = {u'本地': 1, u'国内长途': 2}
            if temp['land_type'] in land_type.keys():
                temp['land_type'] = land_type[temp['land_type']]
            else:
                temp['land_type'] = 3

        if 'call_date' in key:
            # '04-01 11:18:50' 对时间进行分割
            date_time = temp['call_date'].split(' ')
            time_format = time.strftime('%Y-%m', time.localtime())
            if int(date_time[0].split('-')[0]) > int(time_format[-2:]):
                temp['call_date'] = ('{}-'.format(str(int(time_format[:4]) -
                                                      1)) + date_time[0])
            else:
                temp['call_date'] = time_format[:5] + date_time[0]
            # temp['call_date'] = '2016-' + date_time[0]
            temp['call_time'] = date_time[1]

    # end


    def convert_value_note(self, temp):
        """短信记录信息字典 key 转换成统一类型

        :param temp: 需要转换的信息字典
        :return: 转换后的信息字典
        """
        key = temp.keys()

        if 'note_date' in key:
            # '04-01 11:18:50' 对时间进行分割
            date_time = temp['note_date'].split(' ')
            time_format = time.strftime('%Y-%m', time.localtime())
            if int(date_time[0].split('-')[0]) >= int(time_format[-2:]):
                temp['call_date'] = ('{}-'.format(str(int(time_format[:4]) -
                                                      1)) + date_time[0])
            else:
                temp['call_date'] = time_format[:5] + date_time[0]
            temp['note_time'] = date_time[1]

    # end


    def getFiveMonthCall(self):
        """爬取近半年的通话记录和短信记录信息

        :return: 记录信息列表（成功有数据）或结果字典（失败或无数据）
        """
        # """Get the call records of the past five months
        # :return: list (maybe empty)
        # """
        text_seq = list()
        month_seq = getMonthSeq()
        for month in month_seq:
            # print '请耐心等待,正在查询{0}:'.format(month)
            result = self.getMonthCall(month)
            # if result:
            if result['code'] == 2000:
                try:
                    json.loads(result['data'])
                except Exception as e:
                    # print 'month_seq: {}'.format(month)
                    # print e.message
                    text_seq.append((month, result['data']))
                    print '访问{0}成功，但解析错误，错误原因：{1}'.format(month,
                                                                    e.message)
                    continue
                # if u'content' in info:
                #     if u'failMessage' in info['content']:
                #         if u'不可再查询' in info['content']['failMessage']:
                #             break
                text_seq.append((month, result['data']))
                print '访问{0}成功'.format(month)
            else:
                text_seq.append((month, result))
                print '访问{0}失败'.format(month)
                # print '抱歉,查询{0}月通话数据失败'.format(month)
        # for
        else:
            return text_seq
        print(u'当日已无法查询')
        return return_result(2100, [], desc=u'当日查询已达上限（6次）')

    # end

    def getMonthCall(self, month):
        """爬取记录信息封装

        :param month: 需要爬取的月份
        :return: 结果字典
        """
        # """Get the call records according to month
        # :param month: year+month, example:'201602'
        # :return: False/response.text
        # """

        def getUniqueTag():
            """获取记录的第一步的逻辑判断

            :return: 结果字典
            """
            # form = {'month': '201602'}
            # form['month'] = month
            form = dict(month=month)
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/query.jsps'
            self.__headers[
                'Referer'] = 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml'
            options = {'method': 'post', 'url': url, 'form': form,
                       'cookies': self.cookies, 'headers': self.__headers}
            response = Request.basic(options)
            if response:
                try:
                    unique_tag = json.loads(response.text)['attachment'][0][
                        'value']
                    return getMonthRecords(unique_tag)
                except (KeyError, IndexError, Exception) as ex:
                    # print 'unique_tag not found, error:', ex
                    # return False
                    print 'unique_tag error: {}'.format(month)
                    print ex.message
                    return return_result(4100, [], desc=u'getUniqueTag 解析错误')
            else:
                # return False
                return return_result(4000, [], desc=u'getUniqueTag 网络错误')

        # def

        def getMonthRecords(unique_tag):
            """获取记录的第二步的逻辑判断

            :param unique_tag: 相关请求参数
            :return: 结果字典
            """
            form = dict(uniqueTag=unique_tag, monthListType='0', isChange='',
                        startTimeReal='', endTimeReal='', month='',
                        )
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/ajaxRealQuery.jsps'
            # pay attention to "timeout"
            options = {'method': 'post', 'url': url, 'form': form,
                       'cookies': self.cookies, 'timeout': 20,
                       'headers': self.__headers}
            response = Request.basic(options)
            if response:
                if response.status_code == 200:
                    if u'不可再查询' not in response.text:
                        return return_result(2000, response.text,
                                             desc=u'getMonthRecords 成功')
                    else:
                        return return_result(2100, [],
                                             desc=u'getMonthRecords 成功')
                else:
                    return return_result(5000, [response.text],
                                         desc=u'getMonthRecords网络错误: {}'
                                         .format(response.status_code))
            else:
                # return False
                return return_result(4000, [], desc=u'getMonthRecords 网络错误')

        # def
        return getUniqueTag()

    # end

    # def saveItems(self):
    #     """  保存数据到mysql
    #     :return: None
    #     """
    #     valid_num = len(self.user_items)
    #     invalid_num = len(self.call_items)
    #     if valid_num:
    #         dbInsert(config.TABEL_NAME_1, config.COLUMN_USER, self.user_items)
    #     if invalid_num:
    #         dbInsert(config.TABLE_NAME_2, config.COLUMN_CALL, self.call_items)
    #
    #     return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)
        # end


# class


def getNoteCode(phone_attr):
    """ 获取手机动态码
    :param phone_attr: {
        'phone':'xxxxxxxxxx',
        'province':'广东',
        'city':'广州',
        'company':2,
        'password' = 'xxxxxxx'
    }
    :return: dict(code=xxx, temp=xxx)
    """
    if not isinstance(phone_attr, dict):
        raise ValueError(u'参数错误')

    spider = ChinaMobile_GD(phone_attr)
    result = spider.getCode()
    return result
    # if result == 2000:
    #     return dict(code=2000, temp=spider)
    # else:
    #     return dict(code=4444, temp=None)


# end

def loginSys(spider):
    """ 登陆与爬取逻辑判断
    :param spider: the object of ChinaMobile_GD
    :return: 最终结果字典
    """
    # """ 登陆系统
    # :param spider: the object of ChinaMobile_GD
    # :return:
    # """
    if not isinstance(spider, ChinaMobile_GD):
        print 'obj error'
        raise ValueError(u'参数错误')

    # login = spider.login()
    # if login == 2000:  # 登录成功

    login = spider.fetch_cookie()
    if login['code'] == 2000:  # 登录成功
        # login = 2000
        # if login == 2000:
        print u'获取登录 Cookie 成功'
        search = spider.clawAllInfo()  # 爬取内容
        # if search == 2000:
        if search['code'] == 2000:
            print u'爬取内容成功'
            # print spider.saveItems()
            result = dict(
                t_operator_user=spider.user_items,
                t_operator_call=spider.call_items,
                t_operator_note=spider.note_items,
            )
            # spider.browser.close()
            # return dict(code=2000, result=result)
            return return_result(2000, result, search['desc'])
        else:
            print u'爬取内容失败'
            return search
    else:
        # print u'登录失败,失败码:{0}'.format(login)
        # spider.browser.close()
        # return dict(code=login, temp=None) # 密码错误4600,动态码错误4610
        print u'获取登录 Cookie 失败'
        return login


# def testGD():
#     from ..get_phone_attr import getPhoneAttr
#     # phone_num = raw_input(u'请输入广东移动手机号:')
#     # attr = getPhoneAttr(phone_num)
#     # if attr['code'] == 2000:
#     #     phone_attr = attr['data']
#     #     phone_attr['password'] = raw_input(u'请输入服务密码：')
#     #
#     #     code_result = getNoteCode(phone_attr) # 获得手机动态码
#     #     if code_result['code'] == 2000:
#     #         print u'获得手机动态码成功'
#     #         # 获得手机动态码，并调用登陆
#     phone_num = raw_input(u'请输入广东移动手机号:')
#     password = raw_input(u'请输入服务密码：')
#     phone_pwd = raw_input(u'请输入手机动态码:')
#     phone_attrs = dict(phone_num=phone_num, password=password,
#                        phone_pwd=phone_pwd)
#     spider = ChinaMobile_GD(phone_attrs)
#     login_result = loginSys(spider)
#     if login_result['code'] == 2000:
#         result = login_result['result']
#         print result
#     else:
#         print login_result
#         # else:
#         #     print code_result


def send_code(phone_num, password):
    """触发短信验证码

    :param phone_num: 手机号码
    :param password: 服务密码
    :return: 结果字典（成功2000或失败非2000），无需要保存的数据
    """
    from ...public.get_phone_attr import get_phone_attr
    attr = get_phone_attr(phone_num)
    if attr['code'] == 2000:
        phone_attr = attr['data']
        phone_attr['password'] = password
        code_result = getNoteCode(phone_attr)  # 获得手机动态码
        if code_result['code'] == 2000:
            print(u'获得手机动态码成功')
            return code_result
        else:
            return code_result
    else:
        return attr


def login_for_crawler(phone_num, password, phone_pwd):
    """登陆以及记录爬取

    :param phone_num: 手机号码
    :param password: 服务密码
    :param phone_pwd: 手机动态密码
    :return: 结果字典，主要包含三部分：通话记录、短信记录、用户信息
    """
    from ...public.get_phone_attr import get_phone_attr
    attrs = get_phone_attr(phone_num)
    if attrs['code'] == 2000:
        phone_attrs = attrs['data']
        phone_attrs.update(phone_num=phone_num, password=password,
                           phone_pwd=phone_pwd)
        spider = ChinaMobile_GD(phone_attrs)
        login_result = loginSys(spider)
        if login_result['code'] == 2000:
            result = login_result
            # print result
            return result
        else:
            # print login_result
            return login_result
    else:
        return attrs


if __name__ == '__main__':
    # testGD()
    phone_num = '15112643691'
    # phone_num = '17012491662'
    password = '352162'
    phone_pwd = '902215'
    print(send_code(phone_num, password))
    # print(login_for_crawler(phone_num, password, phone_pwd))