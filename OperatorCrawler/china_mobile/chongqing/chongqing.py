# -*-coding:utf-8 -*-


from __future__ import unicode_literals
import re
import PyV8
import json
import datetime
import traceback
from io import BytesIO
from PIL import Image
# 自定义的功能模块
from customize import url_requests
from customize.uf_exception import (CaptchaFailed)
from recognize import image_to_string
from ...public import code_desc

class ChinaMobile_CQ():
    """中国移动-重庆爬虫"""

    def __init__(self, **kwargs):
        self.phone = kwargs.get('phone')          # 手机号码
        self.password = kwargs.get('password')    # 服务密码
        self.cookies = kwargs.get('cookies', {})  # 保存cookies

    # 加密服务密码
    @staticmethod
    def des_core(phone, password):
        """加密服务密码"""

        js_c = PyV8.JSContext()
        js_c.enter()
        js_content = open('securityencode_js.txt').read().decode('utf-8')
        des_js_content = js_content.replace('123456', password)\
                                    .replace('11111111', phone[:8]) \
                                    .replace('22222222', phone[1:9])\
                                    .replace('33333333', phone[3:11])
        value = js_c.eval(des_js_content)
        return value

    # 获取cookies
    def get_cookies(self):
        """返回登录后的cookies"""

        def first_step():
            """获取一个cookie值"""

            url = (
            'http://www.cq.10086.cn/saturn/app?service=page/Home&listener'
            '=getCustInfo&CHAN_ID=E003&TELNUM=&?idsite=1&rec=1&url=https%3A%2F'
            '%2Fservice.cq.10086.cn%2FhttpsFiles%2FpageLogin.html&res=1440x900'
            '&col=24-bit&h=15&m=46&s=10&cookie=1&urlref=&rand=0'
            '.029307082742521917&pdf=1&qt=0&realp=0&wma=0&dir=0&fla=1&java=0'
            '&gears=0&ag=0&action_name=%2525E9%252587%25258D%2525E5%2525BA%252586'
            '%2525E7%2525A7%2525BB%2525E5%25258A%2525A8%2525E7%2525BD%252591'
            '%2525E4%2525B8%25258A%2525E8%252590%2525A5%2525E4%2525B8%25259A'
            '%2525E5%25258E%252585%25257C%2525E5%252585%252585%2525E5%252580'
            '%2525BC%2525EF%2525BC%25258C%2525E7%2525BC%2525B4%2525E8%2525B4'
            '%2525B9%2525EF%2525BC%25258C%2525E4%2525B8%25259A%2525E5%25258A'
            '%2525A1%2525E5%25258A%25259E%2525E7%252590%252586%2525EF%2525BC'
            '%25258C%2525E7%2525BD%252591%2525E4%2525B8%25258A%2525E8%252587'
            '%2525AA%2525E5%25258A%2525A9%2525E6%25259C%25258D%2525E5%25258A'
            '%2525A1%2525EF%2525BC%25258C%2525E7%2525A7%2525BB%2525E5%25258A'
            '%2525A8%2525E6%252594%2525B9%2525E5%25258F%252598%2525E7%252594'
            '%25259F%2525E6%2525B4%2525BB%2525E3%252580%252582')
            headers = {
                'Host': 'service.cq.10086.cn',
                'Referer': 'http://www.10086.cn/cq/index_230_230.html',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/57.0.2987.133 Safari/537.36')
            }
            res = url_requests.get(url, headers=headers)

            self.cookies.update(dict(res.cookies))

        def second_step(cookie):
            """根据first_step获取的cookie，获取第二个cookie并更新"""

            url = 'https://service.cq.10086.cn/ics'

            headers = {
                'Host': 'service.cq.10086.cn',
                'Referer': 'https://service.cq.10086.cn/httpsFiles/pageLogin.html',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/57.0.2987.133 Safari/537.36')
            }

            params = {
                'service': 'ajaxDirect/1/login/login/javascript/',
                'pagename': 'login',
                'eventname': 'checkIsLocalNumberNow',
                'cond_TELNUM': self.phone,
                'ajaxSubmitType': 'get',
                'ajax_randomcode': '20170508150704780.7728731616524849'
            }
            r = url_requests.get(url=url, params=params, headers=headers)

            self.cookies.update(dict(r.cookies))

        def third_step(cookie):
            """用1,2步拿到的cookie去获取验证码图片"""

            url = ('https://service.cq.10086.cn/servlet/ImageServlet')
            headers = {
                'Host': 'service.cq.10086.cn',
                'Referer': 'https://service.cq.10086.cn/httpsFiles/pageLogin.html',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/57.0.2987.133 Safari/537.36')
            }
            res = url_requests.get(url, headers=headers, cookies=cookie)
            f = BytesIO(res.content)
            img = Image.open(f)
            # img.save('trainset/%s.png' % str(i))
            # img.show()
            return img

        def forth_step(phone, password, validate_code, cookies):
            """用验证码+用户名+服务密码去获取一个url，同时更新cookie。"""

            url = 'https://service.cq.10086.cn/ics'
            headers = {
                'Host': 'service.cq.10086.cn',
                'Referer': 'https://service.cq.10086.cn/httpsFiles/pageLogin.html',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/57.0.2987.133 Safari/537.36')
            }
            params = {
                'service': 'ajaxDirect/1/login/login/javascript/',
                'pagename': 'login',
                'eventname': 'SSOlogin',
                'cond_REMEMBER_TAG': 'false',
                'cond_LOGIN_TYPE': '2', # 如果是动态验证码，此处为0
                'cond_SERIAL_NUMBER': phone,
                'cond_USER_PASSWD': ChinaMobile_CQ.des_core(phone, password),
                # ChinaMobile_CQ.des_core(phone, password),
                'cond_USER_PASSSMS': '',    # 动态验证码
                'cond_VALIDATE_CODE': validate_code,
                'ajaxSubmitType': 'post',
                'ajax_randomcode': '20170508112126380.18652078435652464'
            }
            response = url_requests.post(url=url,
                                     params=params,
                                     headers=headers,
                                     cookies=cookies)
            url = ''
            if '验证码不正确' in response.content.decode('utf-8'):
                print '验证码不正确'
            elif '登陆成功' in response.content.decode('utf-8'):
                print '登陆成功'
                self.cookies.update(dict(response.cookies))
                url = re.search('"url":"(.*?)"',
                                response.content, re.S).group(1)
            else:
                print response.content

            return url

        def fifth_step(url, cookie):
            """用第4步请求得到的cookie和url，访问再更新一次cookie，该cookie应该可用与查询数据"""

            headers = {
                'Host': 'login.10086.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.133 Safari/537.36',
                'Referer': 'https://service.cq.10086.cn/httpsFiles/pageLogin.html'
            }
            res3 = url_requests.get(url, headers=headers, cookies=cookie,
                                allow_redirects=False)
            # print res3.cookies
            self.cookies.update(res3.cookies)

        first_step()

        second_step(cookie=self.cookies)
        # 限定验证码的识别次数
        times = 0
        mid_url = ''
        while times < 10:
            print times
            img = third_step(cookie=self.cookies)
            # code = raw_input('please input code: ')
            code = image_to_string(img)
            mid_url = forth_step(phone=self.phone, password=self.password,
                                 validate_code=code, cookies=self.cookies)
            if mid_url:
                break
            else:
                times += 1
        if times == 10:
            raise CaptchaFailed('验证码识别失败')

        fifth_step(url=mid_url, cookie=self.cookies)

        return self.cookies

    # 获取用户信息
    def get_profile(self):
        """4步更新cookies到self.cookies, 再返回用户信息。"""

        def updata1_cookies():
            """update cookies"""

            url = 'http://shop.10086.cn/i/v1/auth/loginfo?_=1493799199065'
            headers = {
                'Host': 'shop.10086.cn',
                'Cache-Control': 'no-store, must-revalidate',
                'pragma': 'no-cache',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.133 Safari/537.36',
                'Referer': 'http://shop.10086.cn/i/'
            }
            response = url_requests.get(url, headers=headers,
                                    cookies=self.cookies)

            self.cookies.update(dict(response.cookies))

        def updata2_cookies():
            """"""

            url = ('https://login.10086.cn/SSOCheck.action?channelID=12003'
                   '&backUrl=http://shop.10086.cn/i/?f=home')
            headers = {
                'Host': 'login.10086.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.133 Safari/537.36',
                'Referer': 'http://shop.10086.cn/i/'
            }
            response = url_requests.get(url, headers=headers,
                                    cookies=self.cookies)

            self.cookies.update(dict(response.cookies))

        def updata3_cookies():
            """"""

            url = ('http://shop.10086.cn/i/v1/auth/getArtifact?artifact'
                   '=e535b790be9c4b028aad1c122816413a&backUrl=http%3A%2F'
                   '%2Fshop.10086.cn%2Fi%2F%3Ff%3Dhome ')
            headers = {
                'Host': 'shop.10086.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.133 Safari/537.36',
                'Referer': 'http://shop.10086.cn/i/'
            }
            response = url_requests.get(url, headers=headers,
                                    cookies=self.cookies)

            self.cookies.update(dict(response.cookies))

        def updata4_cookies():
            """"""

            url = ('http://shop.10086.cn/nresource/image/t_close.gif ')
            headers = {
                'Host': 'shop.10086.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.133 Safari/537.36',
                'Referer': 'http://shop.10086.cn/i/?f=home&welcome=1493799181858'
            }
            response = url_requests.get(url, headers=headers,
                                    cookies=self.cookies)

            self.cookies.update(dict(response.cookies))

        def get_info(phone):
            """获取用户信息"""

            url = ('http://shop.10086.cn/i/v1/cust/mergecust/%s?_'
                  '=1493799201153') % phone
            headers = {
                'Host': 'shop.10086.cn',
                'Cache-Control': 'no-store, must-revalidate',
                'pragma': 'no-cache',
                'X-Requested-With': 'XMLHttpRequest',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                              'AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/57.0.2987.133 Safari/537.36',
                'Referer': 'http://shop.10086.cn/i/?f=home&welcome=1493796456510'
            }
            response = url_requests.get(url, headers=headers,
                                    cookies=self.cookies)
            profile = dict(json.loads(response.content))

            table = {}
            table['name'] = profile['data']['custInfoQryOut']['name']
            table['sex'] = ''
            table['address'] = profile['data']['custInfoQryOut']['address']
            table['cert_type'] = '身份证'
            table['cert_num'] = ''
            table['phone'] = profile['data']['custInfoQryOut']['contactNum']
            table['company'] = '中国移动'
            table['province'] = '重庆市'
            table['city'] = '重庆市'
            table['product_name'] = profile['data']['curPlanQryOut']['curPlanName']
            table['level'] = profile['data']['custInfoQryOut']['starLevel']
            table['open_date'] = profile['data']['custInfoQryOut']['inNetDate']
            table['balance'] = ''
            if profile['data']['custInfoQryOut']['status'] == '00':
                table['user_valid'] = 1
            else:
                table['user_valid'] = 0

            return [table]

        try:
            updata1_cookies()
            updata2_cookies()
            updata3_cookies()
            updata4_cookies()
            info = get_info(self.phone)
        except Exception as e:
            print '获取用户信息失败\n', e.message
            info = [{}]
        return info

    # 触发短信验证码
    def send(self):
        """向客户手机发送短信密码"""

        url = 'https://service.cq.10086.cn/ics'

        headers = {
            'Host': 'service.cq.10086.cn',
            'Referer': 'https://service.cq.10086.cn/httpsFiles/pageLogin.html',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/57.0.2987.133 Safari/537.36')
        }
        params = {
            'service': 'ajaxDirect/1/secondValidate/secondValidate/javascript/',
            'pagename': 'secondValidate',
            'eventname': 'getTwoVerification',
            'GOODSNAME': '用户详单',
            'DOWHAT': 'QUE',
            'ajaxSubmitType': 'post',
            'ajax_randomcode': '20170508150704780.7728731616524849'
        }
        url_requests.post(url=url, params=params,
                          headers=headers, cookies=self.cookies)
        print "send success, please check you message on your phone."

    # 二次验证
    def second_validate(self, passSMS):
        """短信密码二次验证"""

        url = ('http://service.cq.10086.cn/ics')
        headers = {
            'Host': 'service.cq.10086.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/57.0.2987.133 Safari/537.36'),
            'Referer': ('http://service.cq.10086.cn/myMobile/detailBill'
                        '.html')
        }
        params = {
            'service': 'ajaxDirect/1/secondValidate/secondValidate'
                       '/javascript/',
            'pagename':	'secondValidate',
            'eventname': 'checkSMSINFO',
            'cond_USER_PASSSMS': passSMS,
            'cond_CHECK_TYPE': 'DETAIL_BILL',
            'cond_loginType': '2',
            'ajaxSubmitType': 'post',
            'ajax_randomcode': '20170516102847590.8665265559471624'
        }
        response = url_requests.post(url=url, headers=headers,
                                 params=params, cookies=self.cookies)
        if '验证成功' in response.content.decode('utf-8'):
            print '验证成功'
        elif '服务密码输入错误' in response.content.decode('utf-8'):
            print '服务密码输入错误'
        elif '短信验证码已失效' in response.content.decode('utf-8'):
            print '短信验证码已失效'
        else:
            print '网络异常, 短信认证失败。'

    # 获取通话记录
    def get_call_record(self):
        """返回通话记录"""

        def get_record(month):
            """查询某月的通话记录

            :param month: like '201705'
            :return: list
            """

            url = ('http://service.cq.10086.cn/ics')
            headers = {
                'Host': 'service.cq.10086.cn',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/57.0.2987.133 Safari/537.36'),
                'Referer': ('http://service.cq.10086.cn/myMobile/detailBill'
                            '.html')
            }
            params = {
                'service':	'ajaxDirect/1/myMobile/myMobile/javascript/',
                'pagename':	'myMobile',
                'eventname':	'getDetailBill',
                'cond_DETAIL_TYPE':	'3',
                'cond_QUERY_TYPE':	'0',
                'cond_QUERY_MONTH':	month,
                'cond_GOODS_ENAME':	'XFMX',
                'cond_GOODS_NAME':	'消费明细',
                'cond_TRANS_TYPE':	'Q',
                'cond_GOODS_ID':	'2015060500000083',
                'ajaxSubmitType':	'post',
                'ajax_randomcode':	'20170509150221440.6991503923974802'
            }
            response = url_requests.post(url=url, headers=headers,
                                     params=params, cookies=self.cookies)
            result = re.search('\[CDATA\[\[(.*?)\]\]\]>',
                               response.content, re.S).group(1)
            result = json.loads(result)
            record = result['resultData']  # list  一个月的记录
            month_list = []
            for each in record:
                table = {}
                table['cert_num'] = ''   # 身份证号码
                table['phone'] = self.phone     # 手机号
                table['call_area'] = each.get('c1', '') # 通话地点
                table['call_date'] = each.get('c0', '')[:5] # 通话日期
                table['call_time'] = each.get('c0', '')[6:] # 通话时间
                table['call_cost'] = float(each.get('c8', 0.00)) + \
                                     float(each.get('c7', 0.00)) # 通话费用
                table['call_long'] = each.get('c4', '') # 通话时长
                table['other_phone'] = each.get('c3', '')# 对方号码
                table['call_type'] = each.get('c2', '') # 呼叫类型
                table['land_type'] = each.get('c5', '') # 通话类型：本地通话， 省内通话 etc
                month_list.append(table)

            return month_list

        record_list = []        # 用于保存每个月的记录，extend 方法添加
        # 获取当前年月，比如：’201705‘
        date = int(str(datetime.datetime.now())[:7].replace('-', '')) # int
        # 循环最近6个月
        m = 6
        while m > 0:
            try:
                month_list = get_record(date)
                record_list.extend(month_list)
            except Exception as e:
                print '%s月份的通话记录获取失败' % str(date)   # 如发生异常，继续查下一个月
                print traceback.format_exc()
            # 判断date是否是1月份，如果是，在减一个月时应该减89至上一年的12月
            if str(date)[-1] == '1':
                date = date - 89
            else:
                date = date - 1
            m = m - 1

        return record_list

    # 获取短信记录
    def get_message_record(self):
        """返回短信记录"""

        def get_record(month):
            """查询某月的通话记录

            :param month: like '201705'
            :return: list
            """

            url = ('http://service.cq.10086.cn/ics')
            headers = {
                'Host': 'service.cq.10086.cn',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; Win64; x64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/57.0.2987.133 Safari/537.36'),
                'Referer': ('http://service.cq.10086.cn/myMobile/detailBill'
                            '.html')
            }
            params = {
                'service':	'ajaxDirect/1/myMobile/myMobile/javascript/',
                'pagename':	'myMobile',
                'eventname':	'getDetailBill',
                'cond_DETAIL_TYPE':	'5',
                'cond_QUERY_TYPE':	'0',
                'cond_QUERY_MONTH':	month,
                'cond_GOODS_ENAME':	'XFMX',
                'cond_GOODS_NAME':	'消费明细',
                'cond_TRANS_TYPE':	'Q',
                'cond_GOODS_ID':	'2015060500000083',
                'ajaxSubmitType':	'post',
                'ajax_randomcode':	'20170509150221440.6991503923974802'
            }
            response = url_requests.post(url=url, headers=headers,
                                     params=params, cookies=self.cookies)
            result = re.search('\[CDATA\[\[(.*?)\]\]\]>',
                               response.content, re.S).group(1)
            result = json.loads(result)
            record = result['resultData']   # list  一个月的记录
            month_list = []
            for each in record:
                table = {}
                table['cert_num'] = ''  # 身份证号码
                table['phone'] = self.phone     # 手机号码
                table['note_date'] = each.get('c0')[:5] # 短信日期
                table['note_time'] = each.get('c0')[6:] # 短信时间
                table['note_cost'] = each.get('c6', '') # 短信费用
                table['business_type'] = each.get('c4', '') # 业务类型
                table['other_phone'] = each.get('c2') # 对方号码
                month_list.append(table)

            return month_list

        record_list = []  # 用于保存每个月的记录，extend 方法添加
        # 获取当前年月，比如：’201705‘
        date = int(str(datetime.datetime.now())[:7].replace('-', ''))  # int
        # 循环最近6个月
        m = 6
        while m > 0:
            try:
                month_list = get_record(date)
                record_list.extend(month_list)
            except Exception as e:
                print '%s月份的短信记录获取失败' % str(date)  # 如发生异常，继续查下一个月
                print traceback.format_exc()
            # 判断date是否是1月份，如果是，在减一个月时应该减89至上一年的12月
            if str(date)[-1] == '1':
                date = date - 89
            else:
                date = date - 1
            m = m - 1

        return record_list

# 登录并发送验证码到手机
def send_code(**kwargs):
    """登录并触发发送短信验证码

    :phone  电话号码
    ：password  服务密码, 这两个key由后台传过来的key决定
    :return dict  包含cookies
    """

    phone = kwargs.get('phone')
    password = kwargs.get('password')

    spider = ChinaMobile_CQ(phone=phone,
                            password=password)
    # 获取登录cookies
    cookies = spider.get_cookies()

    # 发送验证码
    spider.send()

    return {'cookies': cookies}

# 查询信息
def login_for_crawler(**kwargs):
    """接受后台二次传递过来的数据，包含cookies和SMS密码，进行查询操作

    ：cookies 传递到后台，后台再传回来的cookies
    ：passSMS 短信验证码，key名由后台的传递决定
    ：phone 手机号码，key名由后台的传递决定
    ：password 服务密码，key名由后台的传递决定
    :return dict 包含三个表，每个表一个字典列表
    """

    phone = kwargs.get('phone')
    password = kwargs.get('password')
    passSMS = kwargs.get('passSMS')
    cookies = kwargs.get('cookies', {})

    spider = ChinaMobile_CQ(phone=phone, password=password, cookies=cookies)
    data = {}
    try:
        # 用户信息
        t_operator_user = spider.get_profile()

        # 二次验证
        spider.second_validate(passSMS=passSMS)

        # 通话记录
        t_operator_call = spider.get_call_record()

        # 短信记录
        t_operator_note = spider.get_message_record()

        # 组合数据
        data['t_operator_user'] = t_operator_user
        data['t_operator_call'] = t_operator_call
        data['t_operator_note'] = t_operator_note
        code = 2000
    except Exception as err:
        if isinstance(err, CaptchaFailed):
            code = err.status_code
        code = 4000
    # 调用外层public中的code_desc
    result = code_desc.return_result(code=code, data=data, desc='success')
    return result


if __name__ == '__main__':
    'https://service.cq.10086.cn/httpsFiles/pageLogin.html'
    USER = [
        {
            'phone': '15825909715',  # 王国庆
            'password': '935089'
        },
        {
            'phone': '13637922138',  # 罗光文
            'password': '678114'
        },
        {
            'phone': '15923183075',  # 胡国逃
            'password': '618666'
        },
        {
            'phone': '18223017860',  # He敏
            'password': '458731'
        },
    ]


    cookies = send_code(phone=USER[3]['phone'], password=USER[3]['password'])

    sms = raw_input('please input the SMS on your phone: ')

    data = login_for_crawler(phone=USER[3]['phone'],
                               password=USER[3]['password'],
                               passSMS=sms)

    print 'complete'
