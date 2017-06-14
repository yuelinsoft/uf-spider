#coding=utf-8
from __future__ import unicode_literals
import re
import os
import ast
import json
import time
import pickle
import os.path
import datetime
import requests
import pandas as pd
# depend
import table_sh as Table
import des_sh as DES
from param_month_sh import getDateSeq
# public
from ...public.get_phone_attr import get_phone_attr
from ...public import (Request, get_timestamp, return_result, share_func)

_time_wait = 2
_time_usual = 100
_time_special = 200
PhantomJS_path = "D:\\phantomjs-1.9.8-windows\\phantomjs.exe"
forb_pw = ['123456', '654321']

def compare_date(reS):
    '''
    # 日期可能开头末尾包含小括号，中括号，中间有/.-和汉字等。
    :param reS: 2017年08月01日
    :return: #2017-08-01
    '''
    reP = "19|20\d{2}\D{1,3}\d{1,2}\D{1,3}\d{1,2}"
    pattern1 = re.findall(reP, reS)
    if pattern1 == []:
        return 1# 对于无法识别的字符串，认为是有效卡；只有在判断出日期已经超过当前时间时才返回0.
    else:
        p0 = pattern1[0]
        J = ""
        for j in p0:
            if j.isdigit():
                J=J+str(j)
            else:
                J=J+" "
        p1=J.split()
        now = datetime.datetime.now()
        if now.year <= int(p1[0]):
            return 1
        elif now.month <= int(p1[1]):
            return 1
        elif now.day <= int(p1[2]):
            return 1
        else:
            return 0

def update_cookie(ck_before, ck_after):
    # string to dict, return combine_dict
    cookies_before = requests.utils.dict_from_cookiejar(ck_before) if type(ck_before) != dict else ck_before
    cookies_after = requests.utils.dict_from_cookiejar(ck_after) if type(ck_after) != dict else ck_after
    # print "before keys:", cookies_before.keys()
    # print "after keys:", cookies_after.keys()
    cookies_combine = cookies_after
    for k in cookies_before:
        if k not in cookies_after:
            cookies_combine[k] = cookies_before[k]
    return cookies_combine

class ChinaMobile_SH():
    """中国移动-上海爬虫"""

    # 对于不成功的返回dict，在外层再包成带data的空返回值的。
    def __init__(self, phone_attr):
        #param phone_attr: 手机归属信息
        self.__headers = {
            'Accept': '*/*',
            'User-Agent': share_func.get_UserAgent(),
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
        self.source_value = 'wysso'
        self.login_json = dict()
        self.cookies_before_jtforward = dict()
        self.cookies_after_jtforward = dict()
        self.cookies_combine = dict()

    def get_code(self):
        # 实现发送验证码
        #
        # url = 'https://sh.ac.10086.cn/login'
        # self.__headers['Host'] = 'sh.ac.10086.cn'
        # options = {'method': 'post', 'url': url,
        #            'cookies': self.cookies, 'headers': self.__headers}
        # resp = Request.basic(options)
        #

        print("1. self.phone_attr:", self.phone_attr)
        url_1 = 'https://sh.ac.10086.cn/loginjt'#''http://gd.10086.cn/my/REALTIME_LIST_SEARCH.shtml'
        self.__headers['Referer'] = ''
        params_1 = {'act': '1',
                        'telno': self.phone_attr['phone']
                        }
        options_1 = {'method': 'get', 'url': url_1, 'params': params_1, 'cookies': self.cookies, 'headers': self.__headers, 'allow_redirects': True}
        resp_1 = Request.basic(options_1)
        if resp_1:
            content = resp_1.text
            if '分钟' in content:
                self.cookies = resp_1.cookies
                return dict(code=2000, data=content)
            else:
                return dict(code=4000, func='get_code', desc='no keyword:'+content)
        else:
            return dict(code=4000, func='get_code')

    def login_sys_encryption(self):
        '''
        登录验证，把号码，密码和验证码传过去，之后的返回字段需要用于重确认。
        :return: 返回状态码和描述等。
        '''
        def login():
            print("2. self.phone_attr:", self.phone_attr)
            url_1 = 'https://sh.ac.10086.cn/login'
            self.__headers['Host'] = 'sh.ac.10086.cn'
            options = {'method': 'post', 'url': url_1,
                       'cookies': self.cookies, 'headers': self.__headers}
            resp_1 = Request.basic(options)
            if resp_1:
                content = resp_1.content#change 0419 .text
                p = '/sh/wsyyt/ac/jtforward.jsp\?source=(.*)";<\/script>'
                m = re.search(p, content)#change 0419, string ..encode('utf-8'))
                if m is None:
                    print("[login_sys_encryption.login]not 'source' value here. [source value] will get normal value.")
                else:
                    self.source_value = m.group(1)
                # self.cookies = resp_1.cookies
                return login_des()
            else:
                return dict(code=4000, func='login_sys_encryption.login')

        def login_des():
            print "login system by des encryption way..."
            url_1 = 'https://sh.ac.10086.cn/loginjt'
            data_1 = {
                        'telno': DES.des_enc(self.phone_attr['phone']),
                        'password': DES.des_enc(self.phone_attr['password']),
                        'dtm': DES.des_enc(self.phone_attr['phone_dtm']),
                        'authLevel': '5',
                        'ctype': '1',
                        'decode': '1',
                        'source': 'wsyyt'
            }
            params = {'act': '2'}
            self.__headers['Referer'] = 'https://sh.ac.10086.cn/jtac/loginbox.jsp?al=2&telno='#'https://sh.ac.10086.cn/jtac/loginbox.jsp?al=3&telno=#'
            self.__headers['Host'] = 'sh.ac.10086.cn'
            options = {'method': 'post', 'url': url_1, 'form': data_1, 'params': params,
                       'cookies': self.cookies, 'headers': self.__headers}
            resp_1 = Request.basic(options)#200
            if resp_1:
                try:
                    content = resp_1.text
                    f_content = json.loads(content)
                except:
                    return dict(code=4000, func='login_sys_encryption.login_des', desc='no json content here.')
                # '{"transactionID":"00210201703282129067151000136488","brand":"","artifact":"","result":"1","uid":null,"message":"短信随机码不正确或已过期，请重新获取"}'
                if ('短信随机码' in f_content['message']) or ('动态密码' in f_content['message']):
                    return dict(code=4610, func='login_sys_encryption.login_des')
                elif '密码' in f_content['message']:
                    return dict(code=4600, func='login_sys_encryption.login_des')
                else:
                    # print "传des值的页面返回的cookies：", resp_1.cookies
                    self.cookies = update_cookie(self.cookies, resp_1.cookies)
                    # self.cookies = ck.merge_cookies(self.cookies, resp_1.cookies)# 200 resp compare 302 req
                    self.login_json = f_content
                    return judge_login()
            else:
                return dict(code=4000, func='login_sys_encryption.login_des')

        def judge_login():
            if self.cookies == dict():
                return dict(code=4000, desc='网络错误，cookie 为空')
            else:
                params = {
                    'channelID': str(self.login_json['transactionID'])[:5],
                    'Artifact': str(self.login_json['artifact']),
                    'TransactionID': str(self.login_json['transactionID']),
                    'backUrl': 'http://www.sh.10086.cn/sh/wsyyt/ac/jtforward.jsp?source='+self.source_value+'&uid='+str(self.login_json['uid'])+'&tourl=http://www.sh.10086.cn/sh/service/'
                }
                url = 'https://login.10086.cn/AddUID.action'#line 10
                self.__headers['Host'] = 'login.10086.cn'
                self.__headers['Referer'] = 'https://sh.ac.10086.cn/jtac/loginbox.jsp?al=2&telno='
                self.__headers['Connection'] = 'keep-alive'

                options = {'method': 'get', 'url': url, 'params': params,
                           'cookies': self.cookies, 'headers': self.__headers, 'allow_redirects': False}
                response = Request.basic(options)#302
                if response:
                    if response.cookies:
                        try:
                            # print "302页面返回的cookies：", response.cookies
                            self.cookies = update_cookie(self.cookies, response.cookies)
                            # self.cookies = ck.merge_cookies(self.cookies, response.cookies)
                            return dict(code=2000, desc='网址成功login.')
                        except:
                            return dict(code=4100, func='login_sys_encryption.judge_login', desc='无法合并cookies.')
                    else:
                        self.cookies = self.cookies
                        return dict(code=4100, func='login_sys_encryption.judge_login', desc='cookies获取错误.')
                else:
                    return dict(code=4000, func='login_sys_encryption.judge_login', desc='response is False.')

        return login()

    def get_user_info(self):
        '''
        爬取用户信息info1, info2。
        requests user info1:
            'name': 'loginName',
            'phone': 'loginMobil'
        [add]: company, province, city, cert_type.
        requests user info2:
            'level': 'credit_level',
            'balance': 'usable_fee',
            'user_valid': 'star_expdate'
        :return:  返回状态码和描述等，详细数据直接调取self.user_items 。
        '''

        def sys_check_login_again():
            '''
            get_user_info1 and get_user_info2 的返回主要是desc需要被用到。
            '''
            t_start = time.time()
                    #######  req 1 begin  ##########line 11
            params = {
                    'source': self.source_value,
                    'uid': str(self.login_json['uid']),
                    'tourl': 'http://www.sh.10086.cn/sh/service/',
            }
            url = 'http://www.sh.10086.cn/sh/wsyyt/ac/jtforward.jsp'
            self.__headers['Host'] = 'www.sh.10086.cn'
            self.__headers['Referer'] = ''
            options = {'method': 'get', 'url': url, 'params': params, 'cookies': self.cookies,
                       'headers': self.__headers}
            resp_1 = Request.basic(options)
            if resp_1:
                # combine cookies of before_req and after_req.
                self.cookies = update_cookie(self.cookies, resp_1.cookies)# old here
                info1_desc = get_user_info1()
                info2_desc = get_user_info2()
                print('[LOGGING-Statistics]spider of get_user_info taked seconds: %s' % (time.time() - t_start))
                print("check user_items: ",self.user_items)
                if self.user_items == list():
                    return dict(code=4000, desc=info1_desc+info2_desc)
                else:
                    return dict(code=2000, desc=info1_desc+info2_desc)
                # return dict(code=2000, desc='')#, desc=info1_desc+info2_desc)
            else:
                return dict(code=4000, desc='sys_check_login_again: resp 1 false.')

        def get_user_info1():
            params = {'act': 'my.getUserName'}
            url = 'http://www.sh.10086.cn/sh/wsyyt/action'
            self.__headers['Referer'] = 'http://www.sh.10086.cn/sh/my/'
            self.__headers['Host'] = 'www.sh.10086.cn'
            options = {'method': 'post', 'url': url, 'params': params,
                       'cookies': self.cookies, 'headers': self.__headers}
            response = Request.basic(options)
            if response:
                try:
                    content = response.text
                    info_1 = ast.literal_eval(content)['value']
                except:
                    return str("get_user_info1: has no key [value] in it. ")
                if info_1 == {}:
                    return "get_user_info1: "+content
                else:
                    item = dict(
                        name=info_1['loginName'] if info_1.has_key('loginName') else '',
                        phone=info_1['loginMobil'] if info_1.has_key('loginMobil') else '',
                        company=self.phone_attr['company'],
                        province=self.phone_attr['province'],
                        city=self.phone_attr['city'],
                        cert_type = '身份证'
                    )
                    self.user_items.append(item)  # 保存记录
                    return str('get_user_info1: success.')
            else:
                return str('get_user_info1: response is false. ')

        def get_user_info2():
            params = {'act': 'my.getmycredit'}
            url = 'http://www.sh.10086.cn/sh/wsyyt/action'
            self.__headers['Referer'] = 'http://www.sh.10086.cn/sh/my/'
            self.__headers['Host'] = 'www.sh.10086.cn'
            options = {'method': 'post', 'url': url, 'params': params,
                       'cookies': self.cookies, 'headers': self.__headers}
            response = Request.basic(options)
            if response:
                try:
                    content = response.text
                    info_2 = ast.literal_eval(content)['value']
                except:
                    return str("get_user_info2: has no key [value] in it. ")
                if info_2 == {}:
                    return "get_user_info2: "+content
                else:
                    item = dict(
                        level=info_2['credit_level'] if info_2.has_key('credit_level') else '',
                        balance=info_2['usable_fee'] if info_2.has_key('usable_fee') else '',
                        user_valid=compare_date(info_2['star_expdate']) if info_2.has_key('star_expdate') else 1,
                    )
                    self.user_items[0].update(item) # 保存记录
                    return str('get_user_info2: success.')
            else:
                return str('get_user_info2: response is false. ')

        return sys_check_login_again()

    def get_call_info(self):
        '''
        通话记录获取与解析返回。
        :return: 返回key中包括code和desc，不包括func，详细数据直接调取self.call_items 。
        '''
        def claw_page_call(date_tuple, data, page_params, clen, ck, resend = 2):
            if False:# just for test count_i
                return dict(code=2000, data=[], desc='[claw_page_call]get data success: ' + date_tuple[0] + date_tuple[1])
            url_call = 'http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do'
            self.__headers['Referer'] = 'http://www.sh.10086.cn/sh/wsyyt/busi/2002_14.jsp'
            self.__headers['Host'] = 'www.sh.10086.cn'
            self.__headers['Content-Length'] = clen
            options_call = {'method': 'post', 'url': url_call, 'form': data,
                       'params': page_params, 'cookies': ck, 'headers': self.__headers}

            resp_call = Request.basic(options_call)
            if resp_call == False and resend > 0:
                print '[LOGGING-warning]page of this month load unsuccessd and reloading now! : ',date_tuple[0], date_tuple[1]
                return claw_page_call(date_tuple, data, page_params, clen, ck, resend - 1)  # 繁忙重传
            elif resp_call == False or ('请重新' in resp_call.text) or ('has moved' in resp_call.text):
                return dict(code=4000, data=[], desc='[claw_page_call]no resp_call: '+date_tuple[0]+date_tuple[1])
            elif resp_call.text == '':
                return dict(code=4000, data=[], desc='[claw_page_call]no resp_call: '+date_tuple[0]+date_tuple[1])
            elif resp_call:
                content = resp_call.content# string type
                p = 'value.?=.*value.?=(.*)value'
                m = re.search(p, content)
                if m is None:
                    return dict(code=4000, data=[], desc='[claw_page_call]re search result is none, may be empty here: '+date_tuple[0]+date_tuple[1])
                else:
                    try:
                        d_list = (m.group(1)).decode('utf-8').split('"')[1]#IndexError: list index out of range
                    except:
                        d_list = (m.group(1)).decode('utf-8').split('"')[0].split(';members')[0].lstrip()
                    d_list = ast.literal_eval(d_list)
                    if len(d_list)==0:
                        return dict(code=2100, data=d_list, desc='[claw_page_call]get data success: '+date_tuple[0]+date_tuple[1])
                    else:
                        print '[LOGGING-note]call page of this month load successd: ', date_tuple[0], date_tuple[1]
                        return dict(code=2000, data=d_list, desc='[claw_page_call]get data success: '+date_tuple[0]+date_tuple[1])
            else:
                return dict(code=4000, data=[], desc='[claw_page_call]no resp_call: '+date_tuple[0]+date_tuple[1])

        def parse_call_info(call_data, count_i):
            if False:# just for test count_i
                if count_i == 6:
                    return dict(code=2000, desc='parse_call_info: success of parse_call_info here.')
                else:
                    return dict(code=2001, desc='[parse_call_info]df no empty and success of parse_call_info here.')
            try:
                df = pd.DataFrame(call_data, columns=Table.LIST_CONVERT_CALL)
            except:
                return dict(code=4000, desc='[parse_call_info]df of call data may be empty here.')
            if df.empty:
                return dict(code=4000, desc='[parse_call_info]df of call data may be empty here.')
            for j in Table.KEY_CONVERT_CALL:
                for k in Table.KEY_CONVERT_CALL[j]:
                    if k in Table.LIST_CONVERT_CALL:
                        try:
                            df.rename(columns = {k:j}, inplace=True)
                        except:
                            print('[LOGGING-warning]may rename unsuccessd in some key and [k, j] is : ',k, j)

            if 'cert_num' in self.user_items:
                a = self.user_items[0]['cert_num']
                df['cert_num'] = pd.Series([a for n in range(len(df.index))], index=df.index)
            else:
                df['cert_num'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

            if 'phone' in self.user_items:
                b = self.user_items[0]['phone']
                df['phone'] = pd.Series([b for n in range(len(df.index))], index=df.index)
            else:
                df['phone'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

            if '起始时间' in df.columns:
                df['call_date'] = pd.Series([str(i).split(' ')[0] for i in df['起始时间']], index=df.index)
                df['call_time'] = pd.Series([str(i).split(' ')[1] for i in df['起始时间']], index=df.index)
            else:
                df['call_date'] = pd.Series(['' for n in range(len(df.index))], index=df.index)
                df['call_time'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

            for i in df.columns:
                if i not in Table.KEY_CONVERT_CALL.keys() and i not in ['cert_num', 'phone', 'call_date', 'call_time']:
                    df = df.drop(i, axis=1)

            df['call_type'] = df['call_type'].map({'主叫': 1, '被叫': 2})
            df['call_type'] = df['call_type'].fillna(3)
            df['call_type'] = df['call_type'].astype(int)
            df['land_type'] = df['land_type'].map({'本地通话': 1, '省内通话': 2})
            df['land_type'] = df['land_type'].fillna(3)
            df['land_type'] = df['land_type'].astype(int)
            self.call_items = df.T.to_dict().values()
            if count_i == 6:
                return dict(code=2000, desc='parse_call_info: success of parse_call_info here.')
            else:
                return dict(code=2001, desc='[parse_call_info]df no empty and success of parse_call_info here.')

        def claw_month_call():
            '''
            claw_page_call 的返回要有确切的月份数据，才可以做append计算；code用于区分2100or非2100。
            parse_call_info 的返回值要有code和desc。
            '''
            date_seq = getDateSeq()
            # date_seq = [['2017-02-01', '2017-02-23', 1]]#, ['2016-10-01', '2016-10-31', 1]]

            call_data = []
            count_i = 0
            desc = ''
            t_start = time.time()
            ck = self.cookies#[0]#for test 0418
            for id, date_tuple in enumerate(date_seq):
                if id == 0:
                    page_params = {'method': 'getOneBillDetailAjax'}
                    data = {
                                'billType': 'NEW_GSM',
                                'startDate': date_tuple[0],
                                'endDate': date_tuple[1],
                                'jingque': '',
                                'searchStr': '-1',
                                'index': '0',
                                'r': get_timestamp(),
                                'isCardNo': '0',
                                'gprsType': ''
                            }
                    clen = 123
                else:
                    page_params = {'method': 'getFiveBillDetailAjax'}
                    data = {
                            'billType': 'NEW_GSM',
                            'startDate': date_tuple[0],
                            'endDate': date_tuple[1],
                            'filterfield': '输入对方号码：',
                            'filterValue': '',
                            'searchStr': '-1',
                            'index': '0',
                            'r': get_timestamp(),
                            'isCardNo': '0',
                            'gprsType': ''
                            }
                    clen = 161
                    ck['WT_FPC'] = 'id='+'2f50fe4eb0f3d86603a1475916109471'+':lv='+get_timestamp()+':ss='+str(int(get_timestamp())+10)
                month_result = claw_page_call(date_tuple, data, page_params, clen, ck)
                month_data = month_result['data']
                call_data = call_data + month_data
                if month_data != [] or month_result['code'] == 2000:
                    count_i = count_i +1
                desc = desc + '\n' +month_result['desc']

            print('[LOGGING-Statistics]spider of call record takes seconds: %s'%(time.time() - t_start))
            parse_code = parse_call_info(call_data, count_i)
            return dict(code=parse_code['code'], desc=desc+parse_code['desc'])

        return claw_month_call()

    def get_note_info(self):
        '''
        短信记录获取与解析返回
        :return:  返回key中包括code和desc，不包括func，详细数据直接调取self.note_items 。
        '''
        def claw_page_note(date_tuple, data, page_params, clen, ck, resend = 2):
            if False:# just for test count_i
                return dict(code=2000, data=[],
                            desc='[claw_page_note]get data success: ' + date_tuple[0] + date_tuple[1])
            url = 'http://www.sh.10086.cn/sh/wsyyt/busi/historySearch.do'
            self.__headers['Referer'] = 'http://www.sh.10086.cn/sh/wsyyt/busi/2002_14.jsp'
            self.__headers['Host'] = 'www.sh.10086.cn'
            self.__headers['Content-Length'] = clen
            options_note = {'method': 'post', 'url': url, 'form': data,
                       'params': page_params, 'cookies': ck, 'headers': self.__headers}

            resp_note = Request.basic(options_note)
            if resp_note == False and resend > 0:
                print '[LOGGING-warning]page of this month load unsuccessd and reloading now! : ',date_tuple[0], date_tuple[1]
                return claw_page_note(date_tuple, data, page_params, clen, ck, resend - 1)  # 繁忙重传
            elif resp_note == False or ('请重新' in resp_note.text) or ('has moved' in resp_note.text):
                return dict(code=4000, data=[], desc='[claw_page_note]no resp_note: '+date_tuple[0]+date_tuple[1])
            elif resp_note.text == '':
                return dict(code=4000, data=[], desc='[claw_page_note]no resp_note: '+date_tuple[0]+date_tuple[1])
            elif resp_note:
                content = resp_note.content # string type
                p = 'value.?=.*value.?=(.*);members\=eval\(value'
                m = re.search(p, content)
                if m is not None:
                    d_list = m.group(1).decode('utf-8')[1:-1]
                else:
                    p = 'value.?=.*value.?=(.*)value'
                    m = re.search(p, content)
                    if m is None:
                        return dict(code=4000, data=[], desc='[claw_page_note]re search result is none, may be empty here: '+date_tuple[0]+date_tuple[1])
                    try:
                        d_list = (m.group(1)).decode('utf-8').split('"')[1]  # m.group(1).split('"')[1]
                    except:
                        d_list = (m.group(1)).decode('utf-8').split('"')[0].split(';members')[0].lstrip()
                d_list = ast.literal_eval(d_list)
                if len(d_list)==0:
                    return dict(code=2100, data=d_list, desc='[claw_page_note]get data success: '+date_tuple[0]+date_tuple[1])
                else:
                    print '[LOGGING-note]note page of this month load successd: ', date_tuple[0], date_tuple[1]
                    return dict(code=2000, data=d_list, desc='[claw_page_note]get data success: '+date_tuple[0]+date_tuple[1])
            else:
                return dict(code=4000, data=[], desc='[claw_page_note]no resp_note: '+date_tuple[0]+date_tuple[1])

        def parse_note_info(note_data, count_i):
            if False:# just for test count_i
                if count_i == 6:
                    return dict(code=2000, desc='parse_note_info: success of parse_note_info here.')
                else:
                    return dict(code=2001, desc='parse_note_info: df no empty and success of parse_call_info here.')
            try:
                df = pd.DataFrame(note_data, columns=Table.LIST_CONVERT_NOTE)
            except:
                return dict(code=4000, desc='parse_note_info: df of note data may be empty here.')
            if df.empty:
                return dict(code=4000, desc='parse_note_info: df of note data may be empty here.')
            else:
                # rename columns
                for j in Table.KEY_CONVERT_NOTE:
                    for k in Table.KEY_CONVERT_NOTE[j]:
                        if k in Table.LIST_CONVERT_NOTE:
                            try:
                                df.rename(columns = {k:j}, inplace=True)
                            except:
                                print('[LOGGING-warning]may rename unsuccessd in some key and [k, j] is : ',k, j)

                if 'cert_num' in self.user_items:
                    a = self.user_items[0]['cert_num']
                    df['cert_num'] = pd.Series([a for n in range(len(df.index))], index=df.index)
                else:
                    df['cert_num'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

                if 'phone' in self.user_items:
                    b = self.user_items[0]['phone']
                    df['phone'] = pd.Series([b for n in range(len(df.index))], index=df.index)
                else:
                    df['phone'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

                if '起始时间' in df.columns:
                    df['call_date'] = pd.Series([str(i).split(' ')[0] for i in df['起始时间']], index=df.index)
                    df['call_time'] = pd.Series([str(i).split(' ')[1] for i in df['起始时间']], index=df.index)
                else:
                    df['call_date'] = pd.Series(['' for n in range(len(df.index))], index=df.index)
                    df['call_time'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

                for i in df.columns:
                    if i not in Table.KEY_CONVERT_NOTE.keys() and i not in ['cert_num', 'phone', 'call_date', 'call_time']:
                        df = df.drop(i, axis=1)

                self.note_items = df.T.to_dict().values()
                if count_i == 6:
                    return dict(code=2000, desc='parse_note_info: success of parse_note_info here.')
                else:
                    return dict(code=2001, desc='parse_note_info: df no empty and success of parse_call_info here.')

        def claw_month_note():
            '''
            claw_page_note 的返回要有确切的月份数据，才可以做append计算；code用于区分2100or非2100。
            parse_note_info 的返回值要有code和desc。
            '''
            date_seq = getDateSeq()
            # date_seq = [['2017-02-01', '2017-02-23', 1]]#, ['2016-10-01', '2016-10-31', 1]]

            note_data = []
            count_i = 0
            desc = ''
            t_start = time.time()
            ck = self.cookies#[0]#for test 0418
            for id, date_tuple in enumerate(date_seq):
                if id == 0:
                    page_params = {'method': 'getOneBillDetailAjax'}
                    data = {
                        'billType': 'NEW_SMS',
                        'startDate': date_tuple[0],
                        'endDate': date_tuple[1],
                        'jingque': '',
                        'searchStr': '-1',
                        'index': '0',
                        'r': get_timestamp(),
                        'isCardNo': '0',
                        'gprsType': ''
                    }
                    clen = 123
                else:
                    page_params = {'method': 'getFiveBillDetailAjax'}
                    data = {
                        'billType': 'NEW_SMS',
                        'startDate': date_tuple[0],
                        'endDate': date_tuple[1],
                        'filterfield': '输入对方号码：',#u'输入对方号码：',
                        'filterValue': '',
                        'searchStr': '-1',
                        'index': '0',
                        'r': get_timestamp(),
                        'isCardNo': '0',
                        'gprsType': ''
                    }
                    clen = 161
                    ck['WT_FPC'] = 'id='+'2f50fe4eb0f3d86603a1475916109471'+':lv='+get_timestamp()+':ss='+str(int(get_timestamp())+10)#'id='+get_ip()+'-1444906800.30581076'+':lv='+str(get_timestamp())+':ss='+str(get_timestamp())
                month_result = claw_page_note(date_tuple, data, page_params, clen, ck)
                month_data = month_result['data']
                note_data = note_data + month_data
                if month_data != [] or month_result['code'] == 2000:
                    count_i = count_i +1
                desc = desc + '\n' +month_result['desc']

            print('[LOGGING-Statistics: spider of note record takes seconds: %s'%(time.time() - t_start))
            parse_code = parse_note_info(note_data, count_i)
            return dict(code=parse_code['code'], desc=desc+parse_code['desc'])

        return claw_month_note()

def check_attr(phone_attr):
    _key = ('phone', 'province', 'city', 'company', 'password')
    if not isinstance(phone_attr, dict) or set(phone_attr.keys()) != set(_key):
        return return_result(4400, data={})
    elif phone_attr['password'] in ['', None]:
        return return_result(4600, data={})
    elif phone_attr['password'] in forb_pw:
        return return_result(7002, data={})
    else: # 参数正确返回True
        return True

def claw_all_info(spider):
    '''
    当成功获取到login cookies之后，开始爬取user info，call info， note info。
    以上三部分信息全部成功时，返回2000；部分成功返回2001；全部不成功按情况返回状态码。
    为了减少log描述合并的工作量，这三部分的返回只包括code跟desc(key desc 均存在)，不包括func和data，data另外取。
    '''
    user_code = spider.get_user_info()
    call_code = spider.get_call_info()
    note_code = spider.get_note_info()
    print user_code
    print call_code
    print note_code
    len_k = len(spider.user_items[0]) if len(spider.user_items) >= 1 else 0
    print('len of user record: %s'%(len_k))#count keys of a dict that in the list
    print('len of call record: %s'%(len(spider.call_items)))
    print('len of note record: %s'%(len(spider.note_items)))

    if [2000, 2000, 2000] == [user_code['code'], call_code['code'], note_code['code']]:
        code = 2000
    elif (2000 in [user_code['code'], call_code['code'], note_code['code']]) \
            or (2001 in [user_code['code'], call_code['code'], note_code['code']]):
        code = 2001
    else:
        code = 4000

    data = dict(
        t_operator_user=spider.user_items,
        t_operator_call=spider.call_items,
        t_operator_note=spider.note_items
    )
    desc=str([user_code['code'], call_code['code'], note_code['code']])+user_code['desc']+call_code['desc']+note_code['desc']
    claw_result = return_result(code=code,data=data, desc=desc)
    return claw_result

# 0.
def send_code(phone_num, password):
    login_cookies = dict()
    attr = get_phone_attr(phone_num)
    if attr['code'] != 2000:
        return login_cookies, return_result(code=4400, data={}, desc='[params fail]may error phone num.')
    phone_attr = attr['data']
    phone_attr['password'] = password
    # phone_attr = {'province': u'', 'phone': phone_num, 'company': 2, 'password': password, 'city': u'\u4e0a\u6d77'}
    check_param = check_attr(phone_attr)
    print 'check_param: ',check_param
    if check_param != True:
        return login_cookies, check_param
    print 'phone_attr: ',phone_attr['city']
    spider = ChinaMobile_SH(phone_attr)
    code_result = spider.get_code()# 获得手机动态码
    return_msg = return_result(
        code=code_result['code'],
        data=code_result['data'] if code_result.has_key('data') else {},
        desc=code_result['desc'] if code_result.has_key('desc') else '',
        func=code_result['func'] if code_result.has_key('func') else ''
    )
    if code_result['code'] == 2000:
        # print('获得手机动态码ing...')
        login_cookies = spider.cookies
        login_cookies = requests.utils.dict_from_cookiejar(login_cookies)
    return login_cookies, return_msg

# 1.
def login_for_crawler(phone_num, password, phone_dtm, login_cookies):
    login_cookies = ast.literal_eval(login_cookies)
    if login_cookies == dict():
        return return_result(code=4400, data={}, desc='[params fail]no cookies here.')
    # login_cookies = requests.utils.cookiejar_from_dict(login_cookies)
    attrs = get_phone_attr(phone_num)
    if attrs['code'] != 2000:#!= 2000
        return return_result(code=4400, data={}, desc='[params fail]may error phone num.')
    phone_attrs = attrs['data']
    phone_attrs['password'] = password
    # phone_attrs = {'province': u'', 'phone': phone_num, 'company': 2, 'password': password, 'city': u'\u4e0a\u6d77'}
    check_param = check_attr(phone_attrs)
    print 'check_param: ',check_param
    if check_param != True:
        return return_result(code=4400, data={}, desc='[params fail]check phone_attrs fail here.')
    phone_attrs.update(phone_dtm=phone_dtm)

    spider = ChinaMobile_SH(phone_attrs)
    t_start_1 = time.time()
    spider.cookies = login_cookies
    login_code = spider.login_sys_encryption()# same as [spider.fetch_cookie()] in gd
    print('[LOGGING-Statistics]login_sys_encryption taked seconds: %s'%(time.time() - t_start_1))
    if login_code['code'] != 2000:#!= 2000
        # login fail and no cookies to get info.
        fail_msg = return_result(
            code=login_code['code'],
            data=login_code['data'] if login_code.has_key('data') else {},
            desc=login_code['desc'] if login_code.has_key('desc') else '',
            func=login_code['func'] if login_code.has_key('func') else ''
        )
        return fail_msg
    cfg = CFG(FOR_TESTING=True)
    try:
        cfg.write_cfg(
            cookies=spider.cookies,
            phone_attr=spider.phone_attr,
            user_items=spider.user_items,
            call_items=spider.call_items,
            note_items=spider.note_items,
            source_value=spider.source_value,
            login_json=spider.login_json,
            cookies_before_jtforward=spider.cookies_before_jtforward,
            cookies_after_jtforward=spider.cookies_after_jtforward,
            cookies_combine=spider.cookies_combine
        )
    except:
        pass
    return claw_all_info(spider)

# ***************************************** For Test ******************************************************

class CFG():
    def __init__(self, TESTING=1, FOR_TESTING=False):
        self.file_cfg = ''
        if TESTING == 2:
            self.file_cfg = r'./'+str(datetime.datetime.now()).split(' ')[0]+'.txt'
        if FOR_TESTING == True:
            self.file_cfg = r'./'+str(datetime.datetime.now()).split(' ')[0]+'.txt'

    def read_cfg(self):
        print('read cfg: %s'%(self.file_cfg))
        try:
            with open(self.file_cfg, 'rb') as f:
                cookies = pickle.load(f)
            return cookies
        except (IOError, EOFError):
            print "no a cookies file here"
            return None

    def write_cfg(self, **kwargs):
        print('write cfg: %s'%(self.file_cfg))
        cfg_P = kwargs
        print 111, cfg_P
        try:
            with open(self.file_cfg, 'wb') as f:
                pickle.dump(cfg_P, f)
        except :
            os.mknod(self.file_cfg)
            with open(self.file_cfg, 'wb') as f:
                pickle.dump(cfg_P, f)

def testSH_1():
    phone_num = ['18717915005', '13764086296', '15900907374', '18202128898', '13916810506', '13501833797'][1]#lei,yue,wu yuan,fengjingli,laoyang,zhousong
    password = ['088652', '930711', '198861', '438023', '610586', '512532'][1]
    # login_1 = Request.basic({'method': 'get', 'url': 'http://www.baidu.com?'})
    # login_cookies = login_1.cookies
    login_cookies, send_result = send_code(phone_num, password)#!!!

    print('step one result:',(login_cookies, send_result))
    if login_cookies != dict():
        phone_dtm = raw_input("pls input dtm: ")
        login_cookies = str(login_cookies)
        print(login_for_crawler(phone_num, password, phone_dtm, login_cookies))
    else:
        print 'may fail in send code step.'

def testSH_2(cfg_P):
    '''
    这个是用来测登录后的信息获取的，比如五个月的通话数据和短信数据
    :param cfg_P:
    :return:
    '''
    spider = ChinaMobile_SH(None)
    spider.cookies = cfg_P["cookies"]
    spider.phone_attr = cfg_P["phone_attr"]
    spider.user_items = cfg_P["user_items"]
    spider.call_items = cfg_P["call_items"]
    spider.note_items = cfg_P["note_items"]
    spider.source_value = cfg_P["source_value"]
    spider.login_json = cfg_P["login_json"]
    spider.cookies_before_jtforward = cfg_P["cookies_before_jtforward"]
    spider.cookies_after_jtforward = cfg_P["cookies_after_jtforward"]
    spider.cookies_combine = cfg_P["cookies_combine"]
    claw_all_info(spider)

if __name__ == '__main__':
    cfg = CFG(TESTING=1)# TESTING 1表示全部测试且存cookies；2表示读cookies且部分测试，一般用于登录后测试。
    if cfg.file_cfg == '':
        testSH_1()
    else:
        cfg_P = cfg.read_cfg()
        print cfg_P
        assert isinstance(cfg_P,dict)
        testSH_2(cfg_P)
        # time.sleep(30)

