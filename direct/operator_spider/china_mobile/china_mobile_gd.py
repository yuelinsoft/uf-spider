#coding=utf-8
from copy import copy
import time
import json
import random
import re
import sys

from lxml import etree
from selenium import webdriver
from selenium.common.exceptions import *
from selenium.webdriver import DesiredCapabilities

from depend.param_month import getMonthSeq
import depend.table as config
from public import (
    Request,
    getUserAgent,
    returnResult,
    password_encryption_based_ras
)


_time_wait = 2
_time_usual = 100
_time_special = 200

capabilities = DesiredCapabilities.PHANTOMJS.copy()
capabilities["phantomjs.page.settings.loadImages"] = False
# phantom_path = r'C:\driver\phantomjs-2.1.1-windows\bin\phantomjs.exe'
phantom_path = r'/home/mao/phantomjs/bin/phantomjs'

class ChinaMobile_GD():
    """中国移动-广东爬虫"""

    def __init__(self, phone_attr):
        #param phone_attr: 手机归属信息
        self.__headers = {
            'Accept': '*/*',
            'User-Agent': getUserAgent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
        }
        self.browser = None
        self.cookies = dict()        # cookies
        self.phone_attr = phone_attr # 手机属性
        self.user_items = list()     # 用户信息
        self.call_items = list()     # 通话信息
        self.note_items = list()     # 短信信息
        self.refresh_num = 3         # 更新峰值
    # end

    @staticmethod
    def getCookies(cookies_seq):
        """ 将selenium获得的cookie序列转为字典
        :return: dict(key=value)
        """
        cookie_dict = dict()
        if cookies_seq:
            for cookie in cookies_seq:
                cookie_dict[cookie['name']] = cookie['value']
        return cookie_dict
    # end


    @staticmethod
    def timeSleep(min=1, max=3):
        # 设置中断
        if min <= max:
            return time.sleep(random.uniform(min, max))
        else:
            raise ValueError('param value error')
    # end

    @staticmethod
    def judgeByMatch(pattern, string):
         # 通过match内容来判断相关类型
        try:
            re.match(pattern, string).group(1)
        except (IndexError, AttributeError):
            return False
        else:
            return True
    # end

    def getCode(self):

        def openBrowser():
            url = 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml'
            # self.browser = webdriver.PhantomJS(r'C:\driver\phantomjs-2.1.1-windows\bin\phantomjs.exe')
            # self.browser = webdriver.Chrome(r'C:\driver\chromedriver.exe')
            self.browser = webdriver.Chrome(r'/usr/bin/chromedriver')
            self.browser.get(url)
            self.browser.implicitly_wait(_time_usual)  # open the login page
            self.timeSleep()
            return True

        def acquireCode():
            try:
                self.browser.switch_to.frame('iframe_login_pop')
            except NoSuchFrameException as frame_ex:
                print frame_ex
                sys.exit(0)
            user_name_element = self.browser.find_element_by_id('mobile')
            user_name_element.clear()
            user_name_element.send_keys(self.phone_attr['phone'])
            try:
                self.browser.find_element_by_id('btn_get_dpw').click()
            except ElementNotVisibleException as ex:
                if self.refresh_num > 0:
                    self.refresh_num -= 1
                    self.browser.refresh()
                    return acquireCode()  # 调用自身
                else:
                    raise Exception(u'对不起,获取手机动态码失败')
            else:
                self.browser.implicitly_wait(_time_usual)  # open the login page
                #　动态密码已发送，10分钟内有效。
                self.timeSleep()
                try:
                    tips = self.browser.find_element_by_xpath('//span[@class="text"]').text.strip().encode('utf-8')
                    print [tips]
                except (NoSuchElementException, WebDriverException):
                    sys.exit(0)
                else:
                    print tips
                    if self.judgeByMatch('(动态密码已发送)', tips):
                        print u'hi,动态验证码已经发送到手机:' + self.phone_attr['phone']
                        return 2000

                    elif self.judgeByMatch('(动态密码发送失败)', tips):
                        print  u'hi,动态验证码无法发送到手机:' + self.phone_attr['phone']
                        return 4000
                    else:
                        print tips
        # # 逻辑
        # if openBrowser():
        #     return acquireCode()
        # else:
        #     raise WebDriverException(u'无法调用驱动')
        def verification_code_trigger():
            form = {'dt': random.randint(1, 99),
                    'mobile': self.phone_attr['phone']}
            url = 'https://gd.ac.10086.cn/ucs/captcha/dpwd/send.jsps'
            self.__headers['Referer'] = ('https://gd.ac.10086.cn/ucs/login/load'
                                         'ing.jsps?reqType=0\&channel=0&cid=100'
                                         '03&area=%2Fcommodity&resource=%2Fcomm'
                                         'odity%2Fservicio%2FservicioForwarding'
                                         '%2FqueryData.jsps&loginType=3&optiona'
                                         'l=false&exp=&backURL=http%3A%2F%2Fgd.'
                                         '10086.cn%2Fmy%2FREALTIME_LIST_SEARCH.'
                                         'shtml')
            self.__headers['X-Requested-With'] = ('XMLHttpRequest')
            options = {'method': 'post', 'url': url, 'form': form,
                       'timeout': 30, 'headers': self.__headers}
            response = Request.basic(options)
            return response if response else False

        def trigger_status():
            response = verification_code_trigger()
            if response:
                if response.status_code == 200:
                    try:
                        info = response.json()
                    except Exception as _:
                        return returnResult(4100, [], desc=u'动态验证码解析错误')
                    if info['type'] == 'SUCCESS_COMPLETE':
                        msg = info['content']
                        return returnResult(2000, [], desc=msg)
                    else:
                        if 'failMessage' in info['content']:
                            msg = info['content']['failMessage']
                        elif 'message' in info['content'][0]:
                            msg = info['content'][0]['message']
                        else:
                            msg = info['content'][0]
                        return returnResult(4800, [], desc=msg)
                else:
                    return returnResult(4000, [],
                                        desc=u'动态验证码请求: {}'
                                        .format(response.status_code))
            else:
                return returnResult(4000, [], desc=u'动态验证码请求网络错误')

        return trigger_status()
    # def

    def login(self):
        user_name_element = self.browser.find_element_by_id('mobile')  # 用户名框
        password_element = self.browser.find_element_by_name('password')  # 密码框
        dynamic_pw_element = self.browser.find_element_by_name('dynamicCaptcha')  # 动态密码框
        login_element = self.browser.find_element_by_id('loginSubmit')  # 登录按钮

        user_name_element.clear()
        user_name_element.send_keys(self.phone_attr['phone'])

        password_element.clear()
        password_element.send_keys(self.phone_attr['password'])

        dynamic_pw_element.send_keys(self.phone_attr['phone_pwd'])
        login_element.click()  # login after click
        self.browser.implicitly_wait(_time_special)
        return self.judgeLogin()  # 登陆态判断
    # def

    def judgeLogin(self):
        """ 进行登录判断
        :return:
        """
        try:
            tips = self.browser.find_element_by_xpath('//span[@class="text"]').text.strip().encode('utf-8')
        except (NoSuchElementException, WebDriverException):
            return 2000
        else:
            print type(tips),len(tips)
            if self.judgeByMatch('(密码)', tips):
                print 'pw error'
                return 4401  # 密码错误
            elif self.judgeByMatch('(动态密码错误)', tips):
                return 4402  # 动态码错误
            elif tips == '':
                return 2000
            else:
                raise Exception(u'未知错误')
    # def

    def encryption_key_request(self):
        form = {
            'loginType': '2',
            'exp': '',
            'cid': '',
            'area': '',
            'resource': '',
            'channel': '0',
            'reqType': '1',
            'optional': 'on',
            'backURL': 'http://gd.10086.cn/service/index.shtml',
        }
        url = 'https://gd.ac.10086.cn/ucs/login/signup.jsps'
        self.__headers['Referer'] = ('https://gd.ac.10086.cn/ucs/login/loading.'
                                     'jsps?backURL=http://gd.10086.cn/service/i'
                                     'ndex.shtml')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers}
        response = Request.basic(options)
        return response if response else False

    def get_encryption_key(self):
        key_response = self.encryption_key_request()
        if key_response:
            if key_response.status_code == 200:
                key_match = re.search(u'"e"\:"(.*?)".*?"n"\:"(.*?)"',
                                      key_response.content.decode('utf-8'))
                try:
                    keys_str = key_match.group(1)
                    mods_str = key_match.group(2)
                    self.cookies = key_response.cookies
                    return keys_str, mods_str
                except Exception as _:
                    return returnResult(4100, [], desc=u'加密 key 解析错误')
            else:
                returnResult(4000, [], desc=u'获取加密 key 网络错误: {}'
                             .format(key_response.status_code))
        else:
            return returnResult(4000, [], desc=u'获取加密 key 网络错误')

    def login_request(self, psw_rsa):
        form = {
            'mobile': self.phone_attr['phone_num'],
            'loginType': '3',
            'password': psw_rsa,
            'dynamicCaptcha': self.phone_attr['phone_pwd'],
            'bizagreeable': 'on',
            'exp': '',
            'cid': '10003',
            'area': '/commodity',
            'resource': '/commodity/servicio/servicioForwarding/queryData.jsps',
            'channel': '0',
            'reqType': '0',
            'backURL': 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml',
        }
        url = 'https://gd.ac.10086.cn/ucs/login/register.jsps'
        self.__headers['Referer'] = ('https://gd.ac.10086.cn/ucs/login/load'
                                     'ing.jsps?reqType=0\&channel=0&cid=100'
                                     '03&area=%2Fcommodity&resource=%2Fcomm'
                                     'odity%2Fservicio%2FservicioForwarding'
                                     '%2FqueryData.jsps&loginType=3&optiona'
                                     'l=false&exp=&backURL=http%3A%2F%2Fgd.'
                                     '10086.cn%2Fmy%2FREALTIME_LIST_SEARCH.'
                                     'shtml')
        self.__headers['X-Requested-With'] = ('XMLHttpRequest')
        options = {'method': 'post', 'url': url, 'form': form,
                   'cookies': self.cookies, 'timeout': 30,
                   'headers': self.__headers}
        response = Request.basic(options)
        return response if response else False

    def session_data_request(self):
        form = {
            'servCode': 'REALTIME_LIST_SEARCH',
            'operaType': 'QUERY',
            'Payment_startDate': '20170120000000',
            'Payment_endDate': '20170120235959',
        }
        url = ('http://gd.10086.cn/commodity/servicio/servicioForwarding'
               '/queryData.jsps')
        self.__headers['Referer'] = ('http://gd.10086.cn/my/REALTIME_LIST_SEAR'
                                     'CH.shtml')
        self.__headers['Host'] = ('gd.10086.cn')
        self.__headers['Origin'] = ('http://gd.10086.cn')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers}
        response = Request.basic(options)
        return response if response else False

    def fetch_session_data(self):
        from requests import cookies

        session_data_response = self.session_data_request()
        if session_data_response:
            if session_data_response.status_code == 200:
                try:
                    self.cookies = cookies.merge_cookies(self.cookies,
                                                         session_data_response
                                                         .cookies)
                    return returnResult(2000, [], desc=u'获取 session_d 成功')
                except:
                    return returnResult(4100, [], desc=u'获取 session_d 解析错误')
            else:
                returnResult(4000, [], desc=u'获取 session_d 网络错误: {}'
                             .format(session_data_response.status_code))
        else:
            return returnResult(4000, [], desc=u'获取 session_d 网络错误')

    def session_request(self):
        form = {}
        url = 'http://gd.10086.cn/common/include/public/isOnline.jsp'
        self.__headers['Referer'] = ('http://gd.10086.cn/my/REALTIME_LIST_SEAR'
                                     'CH.shtml')
        self.__headers['Host'] = ('gd.10086.cn')
        self.__headers['Origin'] = ('http://gd.10086.cn')
        options = {'method': 'post', 'url': url, 'form': form, 'timeout': 30,
                   'headers': self.__headers}
        response = Request.basic(options)
        return response if response else False

    def fetch_session(self):
        from requests import cookies

        session_response = self.session_request()
        if session_response:
            if session_response.status_code == 200:
                try:
                    self.cookies = cookies.merge_cookies(self.cookies,
                                                         session_response
                                                         .cookies)
                    return returnResult(2000, [], desc=u'获取 session 成功')
                except:
                    return returnResult(4100, [], desc=u'获取 session 解析错误')
            else:
                returnResult(4000, [], desc=u'获取 session 网络错误: {}'
                             .format(session_response.status_code))
        else:
            return returnResult(4000, [], desc=u'获取 session 网络错误')

    def get_login_url(self, login_response):
        if login_response:
            if login_response.status_code == 200:
                try:
                    info = login_response.json()
                except Exception as _:
                    return returnResult(4100, [], desc=u'登陆网址解析错误')
                if info['type'] == 'ucs.server.location.url':
                    msg = info['content']
                    self.cookies = login_response.cookies
                    return returnResult(2000, msg, desc=msg)
                else:
                    code = 4800
                    if 'failMessage' in info['content']:
                        msg = info['content']['failMessage']
                    elif 'message' in info['content'][0]:
                        msg = info['content'][0]['message']
                    else:
                        msg = info['content']
                    if msg == u'动态密码错误！':
                        code = 4402
                    elif u'密码错误，请重新输入' in msg:
                        code = 4401
                    return returnResult(code, [], desc=msg)
            else:
                returnResult(4000, [], desc=u'获取登陆网址网络错误: {}'
                             .format(login_response.status_code))
        else:
            return returnResult(4000, [], desc=u'获取登陆网址网络错误')

    def login_url_request(self, login_url):
        url = login_url
        self.__headers['host'] = ('gd.10086.cn')
        self.__headers['Accept'] = ('text/html,application/xhtml+xml,applicati'
                                    'on/xml;q=0.9,image/webp,*/*;q=0.8')
        self.__headers['Upgrade-Insecure-Requests'] = '1'
        options = {'method': 'get', 'url': url, 'timeout': 30,
                   'cookies': self.cookies, 'headers': self.__headers,
                   'allow_redirects': False}
        response = Request.basic(options)
        return response if response else False

    def set_login_cookie(self, login_url):
        from requests import cookies

        login_url_response = self.login_url_request(login_url)
        if login_url_response:
            if login_url_response.status_code == 302:
                if login_url_response.cookies:
                    try:
                        self.cookies = cookies.merge_cookies(self.cookies,
                                                             login_url_response
                                                             .cookies)
                        return returnResult(2000, [], desc=u'登陆网址成功')
                    except:
                        return returnResult(4100, [], desc=u'无法获取 cookie')
                else:
                    return returnResult(4100, [], desc=u'cookie 获取错误')
            else:
                returnResult(4000, [], desc=u'登陆网址网络错误: {}'
                             .format(login_url_response.status_code))
        else:
            return returnResult(4000, [], desc=u'登陆网址网络错误')

    def fetch_cookie(self):
        key_result = self.get_encryption_key()
        if isinstance(key_result, dict):
            return key_result
        else:
            keys_str, mods_str = key_result
        psw_rsa = password_encryption_based_ras(self.phone_attr['password'],
                                                keys_str, mods_str)
        login_response = self.login_request(psw_rsa)
        login_url = self.get_login_url(login_response)
        if login_url['code'] == 2000:
            session_result = self.fetch_session()
            if session_result['code'] == 2000:
                session_data_result = self.fetch_session_data()
                if session_data_result['code'] == 2000:
                    return self.set_login_cookie(login_url['data'])
                else:
                    return session_data_result
            else:
                return session_result
        else:
            return login_url


    def clawAllInfo(self):
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
            return returnResult(4000, [], desc=u'网络错误，cookie 为空')
    # end

    def clawUserInfo(self):
        """Get the basic information of the user
        :return:False/list
        """
        def queryInfo():
            form = {'servCode': 'MY_BASICINFO'}
            url = 'http://gd.10086.cn/commodity/servicio/track/servicioDcstrack/query.jsps'
            self.__headers['Referer'] = 'http://gd.10086.cn/my/myService/myBasicInfo.shtml'
            options = {'method':'post', 'url':url, 'form':form,
                       'cookies':self.cookies, 'headers':self.__headers}
            response = Request.basic(options)
            if response:
                # TODO: auto found
                print(response.text)
                return getInfo()
            else:
                # return False
                return returnResult(4000, [], desc=u'queryInfo 网络错误')
        # def

        def getInfo():
            form = {'servCode':'MY_BASICINFO', 'operaType':'QUERY'}
            url = 'http://gd.10086.cn/commodity/servicio/servicioForwarding/queryData.jsps'
            self.__headers['Referer'] = 'http://gd.10086.cn/my/myService/myBasicInfo.shtml'
            options = {'method':'post', 'url':url, 'form':form,
                       'cookies':self.cookies, 'timeout':30, 'headers':self.__headers}
            response = Request.basic(options)
            if response:
                # return clawInfo(response.text)
                return clawInfo(response.content.decode('utf-8'))
            else:
                # return False
                return returnResult(4000, [], desc=u'getInfo 网络错误')
        # def

        def clawInfo(text):
            try:
                # selector = etree.HTML(text)
                # table = selector.xpath('//table[@class="tb02"]')[0]
                # values =  table.xpath('tbody/tr[2]/td/text()')
                # if len(values) == 0:
                #     values =  table.xpath('tr[2]/td/text()')
                print(u'用户状态', text)
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
                    level=re.search(u"link'\)\.html\('(.*?)'\)",
                                    text).group(1),
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
                self.user_items.append(item) # 保存记录
                return returnResult(2000, [], desc=u'获取客户信息成功')
            except AttributeError:
                # TODO: 确认已登陆
                return returnResult(4100, [], desc=u'获取客户信息解析错误')
            except (IndexError, Exception) as ex:
                # return False
                return returnResult(4000, [], desc=u'获取客户信息网络错误')
        # def
        return queryInfo()
    # end

    def clawCallInfo(self):
        """ Save all call records
        :return: null
        """
        item = {
            'cert_num': self.user_items[0]['cert_num'],
            'phone': self.user_items[0]['phone']
        }
        text_seq = self.getFiveMonthCall()
        # if len(text_seq) > 0:
        desc_list = [u'爬取记录成功，但存在未能爬取信息的月份：']
        for text in text_seq:
            if isinstance(text[1], dict):
                desc_list.append(u'{}, 错误原因: {};'
                                 .format(unicode(text[0]),
                                         unicode(text[1]['desc'])))
            else:
                try:
                    results = json.loads(text[1])['content']['realtimeListSearchRspBean']['calldetail']['calldetaillist']
                    sms_results = (json.loads(text[1])['content']['realtimeListSearchRspBean']['smsdetail']['smsdetaillist'])
                except Exception as e:
                    desc_list.append(u'{}, 错误原因: {};'
                                     .format(unicode(text[0]), unicode(e.message)))
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
                        print ex
                        for k, v in temp.items():
                            print k, v
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
                        print ex
                        for k, v in temp.items():
                            print k, v
                    self.note_items.append(temp)
        if len(desc_list) == 7:
            return returnResult(4000, [], desc=u'爬取记录网络错误')
        elif 7 > len(desc_list) > 1:
            return returnResult(2000, [], desc=''.join(desc_list))
        elif len(desc_list) == 1:
            return returnResult(2000, [], desc=u'爬取记录成功')
        # else:
        #     print 'call records not found'
    # end


    def convertValues(self,temp):
        key = temp.keys()
        if 'call_type' in key:
            call_type = {u'主叫': 1, u'被叫': 2 }
            if temp['call_type'] in call_type.keys():
                temp['call_type'] = call_type[temp['call_type']]
            else:
                temp['call_type'] = 3

        if 'land_type'in key:
            land_type = {u'本地': 1, u'国内长途': 2}
            if temp['land_type'] in land_type.keys():
                temp['land_type'] = land_type[temp['land_type']]
            else:
                temp['land_type'] = 3

        if 'call_date' in key:
            # '04-01 11:18:50' 对时间进行分割
            date_time = temp['call_date'].split(' ')
            # TODO: auto setup
            if int(date_time[0].split('-')[0]) >= 8:
                temp['call_date'] = '2016-' + date_time[0]
            else:
                temp['call_date'] = '2017-' + date_time[0]
            # temp['call_date'] = '2016-' + date_time[0]
            temp['call_time'] = date_time[1]
    # end


    def convert_value_note(self, temp):
        key = temp.keys()

        if 'note_date' in key:
            # '04-01 11:18:50' 对时间进行分割
            date_time = temp['note_date'].split(' ')
            # TODO: auto setup
            if int(date_time[0].split('-')[0]) >= 8:
                temp['note_date'] = '2016-' + date_time[0]
            else:
                temp['note_date'] = '2017-' + date_time[0]
            temp['note_time'] = date_time[1]
    # end


    def getFiveMonthCall(self):
        """Get the call records of the past five months
        :return: list (maybe empty)
        """
        text_seq = list()
        month_seq = getMonthSeq()

        for month in month_seq:
            print '请耐心等待,正在查询{0}:'.format(month)
            result = self.getMonthCall(month)
            # if result:
            if result['code'] == 2000:
                text_seq.append((month, result['data']))
            else:
                text_seq.append((month, result))
                print '抱歉,查询{0}月通话数据失败'.format(month)
        # for
        return text_seq
    # end

    def getMonthCall(self, month):
        """Get the call records according to month
        :param month: year+month, example:'201602'
        :return: False/response.text
        """
        def getUniqueTag():
            # form = {'month': '201602'}
            # form['month'] = month
            form = dict(month=month)
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/query.jsps'
            self.__headers['Referer'] = 'http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml?dt=1469030400000'
            options = {'method':'post', 'url':url, 'form':form,
                       'cookies':self.cookies, 'headers':self.__headers}
            response = Request.basic(options)
            if response:
                try:
                    unique_tag = json.loads(response.text)['attachment'][0]['value']
                    return getMonthRecords(unique_tag)
                except (KeyError,IndexError,Exception) as ex :
                    print 'unique_tag not found, error:',ex
                    # return False
                    return returnResult(4100, [], desc=u'getUniqueTag 解析错误')
            else:
                # return False
                return returnResult(4000, [], desc=u'getUniqueTag 网络错误')
        # def

        def getMonthRecords(unique_tag):

            form = dict(uniqueTag=unique_tag, monthListType='0')
            url = 'http://gd.10086.cn/commodity/servicio/nostandardserv/realtimeListSearch/ajaxRealQuery.jsps'
            # pay attention to "timeout"
            options = {'method':'post', 'url':url, 'form':form,
                       'cookies':self.cookies, 'timeout':20, 'headers':self.__headers}
            response = Request.basic(options)
            if response:
                return returnResult(2000, response.text,
                                    desc=u'getMonthRecords 成功')
            else:
                # return False
                return returnResult(4000, [], desc=u'getMonthRecords 网络错误')
        # def
        return getUniqueTag()
    # end

    def saveItems(self):
        """  保存数据到mysql
        :return: None
        """
        valid_num  = len(self.user_items)
        invalid_num = len(self.call_items)
        if valid_num:
            dbInsert(config.TABEL_NAME_1, config.COLUMN_USER, self.user_items)
        if invalid_num:
            dbInsert(config.TABLE_NAME_2, config.COLUMN_CALL, self.call_items)

        return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)
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
    """ 登陆系统
    :param spider: the object of ChinaMobile_GD
    :return:
    """
    if not isinstance(spider, ChinaMobile_GD):
        print 'obj error'
        raise  ValueError(u'参数错误')

    # login = spider.login()
    # if login == 2000:  # 登录成功

    login = spider.fetch_cookie()
    if login['code'] == 2000: # 登录成功
    # login = 2000
    # if login == 2000:
        print u'登录成功'
        search = spider.clawAllInfo() # 爬取内容
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
            return returnResult(2000, result, search['desc'])
        else:
            return search
    else:
        # print u'登录失败,失败码:{0}'.format(login)
        # spider.browser.close()
        # return dict(code=login, temp=None) # 密码错误4401,动态码错误4402
        return login

def testGD():
    from ..get_phone_attr import getPhoneAttr
    # phone_num = raw_input(u'请输入广东移动手机号:')
    # attr = getPhoneAttr(phone_num)
    # if attr['code'] == 2000:
    #     phone_attr = attr['data']
    #     phone_attr['password'] = raw_input(u'请输入服务密码：')
    #
    #     code_result = getNoteCode(phone_attr) # 获得手机动态码
    #     if code_result['code'] == 2000:
    #         print u'获得手机动态码成功'
    #         # 获得手机动态码，并调用登陆
    phone_num = raw_input(u'请输入广东移动手机号:')
    password = raw_input(u'请输入服务密码：')
    phone_pwd = raw_input(u'请输入手机动态码:')
    phone_attrs = dict(phone_num=phone_num, password=password,
                       phone_pwd=phone_pwd)
    spider = ChinaMobile_GD(phone_attrs)
    login_result = loginSys(spider)
    if login_result['code'] == 2000:
        result = login_result['result']
        print result
    else:
        print login_result
        # else:
        #     print code_result


def send_code(phone_num, password):
    from ..get_phone_attr import getPhoneAttr
    # from get_phone_attr import getPhoneAttr
    attr = getPhoneAttr(phone_num)
    if attr['code'] == 2000:
        phone_attr = attr['data']
        phone_attr['password'] = password
        code_result = getNoteCode(phone_attr) # 获得手机动态码
        if code_result['code'] == 2000:
            print(u'获得手机动态码成功')
            return code_result
        else:
            return code_result
    else:
        return attr


def login_for_crawler(phone_num, password, phone_pwd):
    from ..get_phone_attr import getPhoneAttr
    # from get_phone_attr import getPhoneAttr
    attrs = getPhoneAttr(phone_num)
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
    # phone_num = '13717056791'
    # password = '586934'
    phone_num = '15012491630'
    password = '19901414'
    phone_pwd = '248917'
    # print(send_code(phone_num, password))
    # print(login_for_crawler(phone_num, password, phone_pwd))