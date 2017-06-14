#coding=utf-8
"""
++++++++++++++++描述+++++++++++++++++
联通通话记录爬取
时间：2017/06/07
更新：把原来的operator_spider.controler.phone_distribute搬到这个脚本，改名为china_unicom_controler，逻辑判断也做了修改。
不过后端那边也实现了这部分功能，然后那边其实是直接去调了handle_ChinaUnicom。
++++++++++++++++Over+++++++++++++++++
"""
import re
import json
import time
import glob
import os.path
import shutil
import pandas as pd
from requests.utils import dict_from_cookiejar
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO
# depend
from param_date import getDateSeq
import table as Table
# public
from ..public.get_phone_attr import get_phone_attr
from ..public import (
    get_UserAgent,
    Request,
    get_timestamp,
    return_result
)

code_hash = {
                    '0000': 2000, # 流程成功
                    '4000': 5500, # msg:'系统忙，请稍后再试。'；密码为空时也会出现这个提示。
                    '7001': 7001, # 出现了验证码
                    '7002': 7002, # 密码过于简单，不支持登录
                    '7005': 7005, # 您的号码所属省份系统正在升级，请稍后再试。
                    '7007': 4600, # 用户名或密码错误
                    '7017': 5500, # 7017, 系统忙，请稍后再试。
                    '7217': 5500, # 7217, 系统忙，请稍后再试。
                    '7218': 5500, # 7218, 登录过于频繁，为保障账号安全，请稍后再试！
                    '7999': 5500, # 对方服务器繁忙
                    '7072': 4500, # 账号错误#比如账户频繁登录
                    '7009': 4500  # 账号错误
                }

forb_pw = ['123456', '654321']

class ChinaUnicom(object):
    """中国联通爬虫"""

    def __init__(self, phone_attr):
        self.headers = {
            'Accept': '*/*',
            'User-Agent': get_UserAgent(),
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'gzip, deflate',
            'Connection': 'keep-alive',
        }
        self.cookies = dict()           # "全局"字典
        self.user_items = list()        # 用户信息
        self.call_items = list()        # 通话信息
        self.phone_attr = phone_attr    # 手机基本信息
        self.dir_name = r"../dir_01/"
    # end

    def login_sys(self):
        """ 登录流程(函数嵌套的方式)
        :return: sysCheckLogin()
        """
        def sys_check_login():
            """ 登录检查,更新cookies
            :return: loginByJS()/dict
            """
            url = 'http://iservice.10010.com/e3/static/check/checklogin/?_=' + get_timestamp()
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/call_dan.html?menuId=000100030001'
            options = {'method': 'post', 'url': url, 'cookies': None, 'headers': self.headers}

            response = Request.basic(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                return login_by_js()
            else:
                return dict(code=4000, func='sys_check_login')
        # end

        def login_by_js():
            """ 通过get登录,更新cookies
            :return: judgeLogin(response)/dict()
            """
            params = {
                '_': '1468474921490',   # req_time + 1
                'callback': 'jQuery172000024585669494775475_1468770450339',
                'password': '662670',
                'productType': '01',
                'pwdType': '01',
                'redirectType':	'03',
                'redirectURL': 'http://www.10010.com',
                'rememberMe': '1',
                'req_time': '1468474921489',
                'userName':	'18617112670'
            }
            params['req_time'] = get_timestamp()
            params['_'] = str(int(params['req_time'])+1)
            params['userName'] = self.phone_attr['phone']
            params['password'] = self.phone_attr['password']

            url = 'https://uac.10010.com/portal/Service/MallLogin'
            self.headers['Referer'] = 'http://uac.10010.com/portal/hallLogin'
            options = {'method': 'get', 'url': url, 'params': params, 'cookies': None, 'headers': self.headers}
            # print 11, options
            response = Request.basic(options)
            if response:
                return judge_login(response)
            else:
                return dict(code=4000, func='login_by_js')
        # def

        def judge_login(response):
            """ 对登录response进行分析
            :param response: response obj
            :return: 登录状态码dict()/raise
            """
            try:
                code = re.search(r'resultCode:"(.*?)"', response.text).group(1)
            except (AttributeError,IndexError) as ex:
                return dict(code=4000, func='judgeLogin')
            else:
                if code in code_hash.keys():
                    self.cookies.update(dict_from_cookiejar(response.cookies))
                    return dict(code=code_hash[code])
                else:
                    e = str(response.text.encode("utf-8")).split('(')[1].split(')')[0]
                    raise Exception(e)
        # def
        return sys_check_login()#1100
    # end

    def get_user_info(self):
        """
        爬取用户信息info1, info2。
        :return:  返回状态码和描述等，详细数据直接调取self.user_items 。
        """
        def sys_check_login_again():
            '''
            get_user_info1 and get_user_info2 的返回主要是desc需要被用到。
            '''
            t_start = time.time()
            url = 'http://iservice.10010.com/e3/static/check/checklogin/?_=' + get_timestamp()
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/call_dan.html?menuId=000100030001'
            options = {'method': 'post', 'url': url, 'cookies': self.cookies, 'headers': self.headers}

            response = Request.basic(options)
            # print 'sys_check_login_again: ',response.content
            if response:
                info1_desc = get_user_info1()
                info2_desc = get_user_info2()
                print('[LOGGING-Statistics]spider of get_user_info taked seconds: %s' % (time.time() - t_start))
                if self.user_items == list():
                    return dict(code=4000, desc=info1_desc + '\n' + info2_desc)
                else:
                    return dict(code=2000, desc=info1_desc + '\n' + info2_desc)
            else:
                return dict(code=4000, desc='sys_check_login_again: resp 1 false.')

        def get_user_info1():
            """ 获得账户balance(余额)self.phone_attr['balance']
            """
            url = 'http://iservice.10010.com/e3/static/query/headerView'
            self.headers['Referer'] = 'http://iservice.10010.com/e3/index_server.html'
            options = {'method': 'post', 'url': url, 'cookies': self.cookies, 'headers': self.headers}

            response = Request.basic(options)
            # print 'get_header_view: ',response.content
            if response:
                try:
                    info_1 = json.load(response.text)['result']
                except:
                    return str("get_user_info1: has no key 'result' in it. ")
                if info_1 == {}:
                    return "get_user_info1: "+str(response.text)
                else:
                    self.phone_attr['balance']=info_1['account'] if info_1.has_key('account') else ''
                    return str('get_user_info1: success.')
            else:
                return str('get_user_info1: response is false.')

        def get_user_info2():
            """ 获得用户信息
            """
            params = { '_':get_timestamp(), 'menuid':'000100030001'}
            url = 'http://iservice.10010.com/e3/static/query/searchPerInfo/'
            self.headers['Referer'] = 'http://iservice.10010.com/e3/query/personal_xx.html'
            options = {'method': 'post', 'url': url, 'params': params, 'cookies': self.cookies, 'headers': self.headers}
            response = Request.basic(options)
            if response:
                item = dict()
                try:
                    result = json.loads(response.text)['result']
                except:
                    return str("get_user_info2: has no key 'result' in it. ")
                if result == {}:
                    return "get_user_info2: "+str(response.text)
                else:
                    try:
                        item['user_valid'] = 1 if result['usercirclestatus'] == u'有效期' else 0
                    except KeyError:
                        item['user_valid'] = 1

                    for k, v in result['MyDetail'].items():
                        if k in Table.KEY_CONVERT_USER.keys():
                            columm_name = Table.KEY_CONVERT_USER[k]
                            item[columm_name] = v
                    del self.phone_attr['password']
                    self.user_items.append(dict(item, **self.phone_attr))
                    return str('get_user_info2: success. ')
            else:
                return str('get_user_info2: response is false.')

        return sys_check_login_again()

    def get_call_info(self):
        '''
        版本更新备忘：
        gevent in month --> download_xlsx；
        原先的coroutine_claw_page_call和convertValues不用了；
        原先的parse_call_info变为解析xlsx的。
        :return: 返回状态码和描述等，详细数据直接调取self.call_items 。
        '''
        def claw_page_call(date_tuple, resend = 2):
            '''
            download xlsx in every month
            :return:
            '''
            params_page = { '_': '1468549625712', 'menuid': '000100030001'}
            form_page = {'pageNo': '1', 'pageSize': '20', 'beginDate': '2016-07-01', 'endDate': '2016-07-18'}
            form_page['pageNo'] = 1
            form_page['beginDate'] = date_tuple[0]
            form_page['endDate'] = date_tuple[1]
            params_page['_'] = get_timestamp()
            url_page = 'http://iservice.10010.com/e3/static/query/callDetail'
            self.headers['Referer'] = 'http://iservice.10010.com/' \
                                      'e3/query/call_dan.html?menuId=000100030001'

            options_page = {'method': 'post', 'url': url_page, 'form': form_page,
                       'params': params_page, 'cookies': self.cookies, 'headers': self.headers}

            t_start_1 = time.time()
            resp_page = Request.basic(options_page)
            # print('[LOGGING-Statistics]spider of call page 1 takes seconds: %s'%(time.time() - t_start_1))####
            if (resp_page == False or 'errorMessage' in str(resp_page.content)) and resend > 0:  # 存在系统繁忙
                print '[LOGGING-warning]page of this month load unsuccessd and reloading now! : ',date_tuple[0], date_tuple[1]
                return claw_page_call(date_tuple, resend - 1)  # 繁忙重传
            if resp_page:
                print '[LOGGING-note]page of this month load successd: ', date_tuple[0], date_tuple[1]
                params_xls = { 'type': 'sound'}
                url_xls = 'http://iservice.10010.com/e3/ToExcel.jsp'
                self.headers['Referer'] = 'http://iservice.10010.com/e4/query/bill/call_dan-iframe.html'

                options_xls = {'method': 'get', 'url': url_xls, 'params': params_xls, 'cookies': self.cookies, 'headers': self.headers}

                t_start_2 = time.time()
                resp_xls = Request.basic(options_xls)
                print('[LOGGING-Statistics]spider of download this xls takes seconds: %s'%(time.time() - t_start_2))
                if resp_xls:
                    try:
                        f = resp_xls.headers['content-disposition'].split('=')[1].decode('utf8')
                        file_name = self.dir_name + f
                        with open(file_name, "wb") as code:
                            code.write(resp_xls.content)
                        print '[LOGGING-note]xls of this month download successd : ',date_tuple[0], date_tuple[1], f
                        return dict(code=2000, data=True, desc='claw_page_call -- download data success: ' + date_tuple[0] + date_tuple[1])
                    except Exception as e:
                        print '[LOGGING-warning]xls of this month download unsuccessd! : ',date_tuple[0], date_tuple[1], e
                        return dict(code=4000, data=False, desc='claw_page_call -- download data unsuccessd: ' + date_tuple[0] + date_tuple[1])
                else:
                    return dict(code=4000, data=False, desc='claw_page_call -- no resp_call 2 xlsx: '+date_tuple[0]+date_tuple[1])
            else:
                return dict(code=4000, data=False, desc='claw_page_call -- no resp_call 1: '+date_tuple[0]+date_tuple[1])

        def parse_call_info(ct):
            # 多个DataFrame相加，不做排序
            # 修改列名；增加四列：cert_num，phone, call_date, call_time；去掉不需要的列；转为list_of_dict
            # 删除文件夹xls_temp

            df = pd.DataFrame()
            for file_name in glob.glob(self.dir_name + "*.xls"):
                try:
                    df_0 = pd.read_excel(file_name)
                    df = df.append(df_0, ignore_index=True)
                except Exception as e:
                    ct = ct - 1
                    print '[LOGGING-warning]xls of this one open unsuccessd! : ',file_name, e
            if df.empty:
                if os.path.exists(self.dir_name):
                    shutil.rmtree(self.dir_name)
                return dict(code=4000, desc='parse_call_info: df of call data may be empty here.')
            for i in df.columns:# a list of col_name
                for k in Table.KEY_CONVERT_CALL:
                    try:
                        if i in Table.KEY_CONVERT_CALL[k]:
                            df.rename(columns = {i: k}, inplace=True)
                    except:
                        print '[LOGGING-warning]may rename unsuccessd in some key and [i] is : ',i

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

            if u'通话起始时间' in df.columns:
                df['call_date'] = pd.Series([str(i).split(' ')[0] for i in df[u'通话起始时间']], index=df.index)
                df['call_time'] = pd.Series([str(i).split(' ')[1] for i in df[u'通话起始时间']], index=df.index)
            else:
                df['call_date'] = pd.Series(['' for n in range(len(df.index))], index=df.index)
                df['call_time'] = pd.Series(['' for n in range(len(df.index))], index=df.index)

            for i in df.columns:
                if i not in Table.KEY_CONVERT_CALL.keys() and i not in ['cert_num', 'phone', 'call_date', 'call_time']:
                    df = df.drop(i, axis=1)

            df['call_type'] = df['call_type'].map({u'主叫': 1, u'被叫': 2})
            df['call_type'] = df['call_type'].fillna(3)
            df['call_type'] = df['call_type'].astype(int)
            df['land_type'] = df['land_type'].map({u'本地通话': 1, u'省内通话': 2})
            df['land_type'] = df['land_type'].fillna(3)
            df['land_type'] = df['land_type'].astype(int)

            self.call_items = df.T.to_dict().values()

            if os.path.exists(self.dir_name):
                shutil.rmtree(self.dir_name)

            if ct == 6:
                return dict(code=2000, desc='parse_call_info: success of parse_call_info here.')
            else:
                return dict(code=2001, desc='parse_call_info: df no empty and success of parse_call_info here.')

        def claw_month_call():
            '''
            claw_page_call 的返回要有确切的月份数据描述True or False，才可以做i的加计算。
            parse_call_info 的返回值要有code和desc,如果需要判断2100也在这一部分。
            '''
            if os.path.exists(self.dir_name) == False:
                os.mkdir(self.dir_name)
            date_seq = getDateSeq()
            # date_seq = [['2017-02-01', '2017-02-23', 1]]#, ['2016-10-01', '2016-10-31', 1]]

            i = 0
            desc = ''
            t_start = time.time()
            for date_tuple in date_seq:
                month_result = claw_page_call(date_tuple)
                if month_result['data'] == True:
                    i = i +1
                desc = desc + '\n' +month_result['desc']

            print('[LOGGING-Statistics]spider of call record takes seconds: %s'%(time.time() - t_start))
            parse_code = parse_call_info(i)
            return dict(code=parse_code['code'], desc=desc+parse_code['desc'])

        return claw_month_call()

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
    目前爬取user info，call info。 note info 部分还没有实现。
    以上两or三部分信息全部成功时，返回2000；部分成功返回2001；全部不成功按情况返回状态码。
    为了减少log描述合并的工作量，这两or三部分的返回只包括code跟desc(key desc 均存在)，不包括func和data，data另外取。
    '''
    user_code = spider.get_user_info()
    call_code = spider.get_call_info()
    print('len of user record: %s'%(len(spider.user_items[0])))#count keys of a dict that in the list
    print('len of call record: %s'%(len(spider.call_items)))
    if [2000, 2000] == [user_code['code'], call_code['code']]:
        code = 2000
    elif (2000 in [user_code['code'], call_code['code']]) or (2001 in [user_code['code'], call_code['code']]):
        code = 2001
    else:
        code = 4000

    data = dict(
        t_operator_user=spider.user_items,
        t_operator_call=spider.call_items,
        t_operator_note=list()
    )
    ### up 0608
    # del: + '...[note record crawler]this spider untapped this moment...'
    desc = 'user code - :'+str(user_code['code'])+'\n'+\
           'call code - :'+str(call_code['code'])+'\n'+\
           user_code['desc'] + call_code['desc']
    claw_result = return_result(code=code, data=data, desc=desc)
    return claw_result

def handle_ChinaUnicom(phone_attr):
    """
    :param phone_attr: dict(phone=XX, province=XX, city=XX, company=XX, password=XX)
    :param password: 全为数字的字符串(长度不少于6位)
    :return:
    """
    check_param = check_attr(phone_attr)
    if check_param != True:
        return check_param  # 返回参数错误

    spider = ChinaUnicom(phone_attr)
    start = time.time()
    login = spider.login_sys()
    print('[LOGGING-Statistics]login_sys taked seconds: %s'%(time.time()-start))
    if login['code'] != 2000:
        fail_msg = return_result(
            code=login['code'],
            data=login['data'] if login.has_key('data') else {},
            desc=login['desc'] if login.has_key('desc') else '',
            func=login['func'] if login.has_key('func') else ''
        )
        return fail_msg
    return claw_all_info(spider)

# def china_unicom_controler(phone, password):
#     '''
#     本函数原来名字叫phone_distribute，功能也做了一些更改。
#     '''
#     phone_attr = get_phone_attr(phone)
#     if phone_attr['code'] == 2000:
#         phone_attr = phone_attr['data']
#         phone_attr['password'] = password
#         return handle_ChinaUnicom(phone_attr)
#     else:
#         return return_result(
#             code=4400,
#             data={},
#             desc=u'查询手机属性外部接口失败'
#         )

# ***************************************** For Test ******************************************************

def for_attr(phone, password):
    '''
    主要是把get_phone_attr给封装一下，因为web接口那边是调取的phone_distribute下的get_phone_attr之后，
    再调取的handle_ChinaUnicom的。所以直接测这个文件的话，test里头就会先调用for_attr这个函数了。
    '''
    phone_attr_1 = get_phone_attr(phone)
    if phone_attr_1['code'] == 2000:
        phone_attr = phone_attr_1['data']
        phone_attr['password'] = password
        print "phone_attr: ",phone_attr
        return  phone_attr
    else:
        return None

def test(phone, password):
    # phone_attr = for_attr(phone, password)
    phone_attr = {'province': u'\u6e56\u5317', 'phone': phone, 'company': 1, 'password': password, 'city': u'\u8346\u5dde'}
    if phone_attr == None:# 重要的判断
        return dict(code=4400, data={}, desc=u'参数错误：应该是手机号问题。')
    check_param = check_attr(phone_attr)
    print 'check_param: ',check_param
    if check_param != True:
        return check_param  # 返回参数错误
    spider = ChinaUnicom(phone_attr)
    start = time.time()
    login = spider.login_sys()
    print('[LOGGING-Statistics]login_sys taked seconds: %s'%(time.time()-start))
    if login['code'] != 2000:
        fail_msg = return_result(
            code=login['code'],
            data=login['data'] if login.has_key('data') else {},
            desc=login['desc'] if login.has_key('desc') else '',
            func=login['func'] if login.has_key('func') else ''
        )
        return fail_msg
    return claw_all_info(spider)

if __name__ == "__main__":
    # web端调取的是controler的phone_distribute，但测试本脚本时会跳过handle_ChinaUnicom函数。
    phone = ['15572031603', '18651234517', '18578410010'][0]
    password = ['150725', '186512', '410011'][0]
    for i in range(1):
        print(test(phone, password))
        # time.sleep(30)

