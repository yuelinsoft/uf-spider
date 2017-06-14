#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2017/3/21 15:38
@Author  : yading
Theme   :spider/direct/operator_spider/china_mobie.py
"""

import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import json
import re
from bs4 import BeautifulSoup
from requests.utils import dict_from_cookiejar
from param_month import getMonthSeq,get_firstday_of_month,get_lastday_of_month
from public.get_phone_attr import get_phone_attr
from public import (
Request,return_result
)

class ChinaMobile_JS():
    """中国移动-江苏爬虫"""

    def __init__(self,phone_num,password):
        self.phone_num=phone_num
        self.password=password

        self.cookies=None
        self.headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        }

    def LoingVsy(self):
        url="http://service.js.10086.cn/actionDispatcher.do"
        form_data={
            'userLoginTransferProtocol':'https',
            'redirectUrl': 'my/MY_QDCX.html?t=1490234778114#home',
            'reqUrl':'login',
            'busiNum': 'LOGIN',
            'operType': '0',
            'passwordType': '1',
            'isSavePasswordVal': '0',
            'isSavePasswordVal_N': '1',
            'currentD': '1',
            'loginFormTab': '#home',
            'loginType': '1',
            'phone-login': 'on',
            'mobile':'18800566440',
            'city': 'NJDQ',
            'password':'188188',
            'verifyCode':'',
        }
        form_data['mobile']=self.phone_num
        form_data['password']=self.password
        self.headers['Origin']='http://service.js.10086.cn'
        self.headers['Host']='service.js.10086.cn'
        self.headers["Referer"]='http://service.js.10086.cn/login.html?url=http://service.js.10086.cn/index.html'
        options = {'method': 'post', 'url': url, 'form':form_data,
                   'params': None, 'cookies':self.cookies, 'headers': self.headers,'timeout':30}
        response=Request.basic(options=options)
        if response:
            if response.status_code==200:
                if 'login.html' not in response.content:
                    #self.cookies=dict_from_cookiejar(response.cookies)
                    self.cookies=response.cookies
                    return return_result(code=2000,data=self.cookies,
                                         desc=u"登录成功!!!")
                else:
                    return return_result(code=4600, data="None",
                            desc=u"phone:{}password:{}用户名或密码错误".format(
                                self.phone_num,self.password))
            else:
                return return_result(code=4000, data="None", desc=u"{}登录请求网络错误".format(
                    self.phone_num))
        else:
            return_result(code=4000, data="None", desc=u"{}登录请求网络错误".format(
                self.phone_num))

        # 查询通话记录时获取验证码的请求
    def getmsgcode(self):
            from requests import cookies
            url = "http://service.js.10086.cn/my/sms.do"
            form_data = {
                "busiNum": "QDCX"
            }
            self.headers[
                "Referer"] = "http://service.js.10086.cn/my/MY_QDCX.html?t=1490249727911"
            self.headers["Origin"] = "http://service.js.10086.cn"
            self.headers["Host"] = "service.js.10086.cn"

            options = {'method': 'post', 'url': url, 'form': form_data,
                       'params': None, 'cookies': self.cookies, 'headers':self.headers,'timeout': 30}
            response = Request.basic(options)
            if response:
                if response.status_code == 200:
                    result_dict = json.loads(response.content)
                    if result_dict['success'] == True:
                        self.cookies = cookies.merge_cookies(self.cookies,
                                                             response.cookies)
                        self.cookies=dict_from_cookiejar(self.cookies)
                        return return_result(code=2000, data=self.cookies,
                                             desc=u"获取短信验证码成功")
                    else:
                        return return_result(code=4000, data=None,
                                             desc=u"获取短信验证码失败!!!")
                else:
                    return return_result(code=4000, data=None, desc=u"{"
                                                             u"}用户短信验证码请求失败!!!".format(
                        self.phone_num))
            else:
                return return_result(code=4000, data=None, desc=u"{"
                                                             u"}用户短信验证码请求失败!!!".format(
                        self.phone_num))

#新建一个用类来爬爬取数据
class Crawlinfo(object):
    __t_operator_call = []
    __t_operator_note = []
    __t_operator_user = []
    __user_dict = {}
    __result_data = {}
    # 定义一个属性用来判断是部分有数据还是全部有数据
    __judge_clist = range(6)
    __judge_nlist = range(6)

    def __init__(self,phone_num,cookiesstr):
        self.phone_num=phone_num
        self.cookies=cookiesstr
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        }

    #首次获取通话记录的第一次请求
    def getphonemsgfirst(self,msgnum,dict_param):
        url="http://service.js.10086.cn/my/actionDispatcher.do"
        form_data={
            'reqUrl':'MY_QDCXQueryNew',
            'busiNum':'QDCX',
            'queryMonth':dict_param['mon'],
            'queryItem':'1',
            'qryPages':'',
            'qryNo':'1',
            'operType':'3',
            'queryBeginTime':dict_param['fday'],
            'queryEndTime':dict_param['lday'],
            'smsNum':msgnum,
            'confirmFlg':'1'
        }
        self.headers["Referer"]="http://service.js.10086.cn/my/MY_QDCX.html?t=1490249727911"
        self.headers["Origin"]="Origin: http://service.js.10086.cn"
        self.headers["Host"]="service.js.10086.cn"

        options = {'method': 'post', 'url': url, 'form': form_data,
                   'params': None, 'cookies': self.cookies, 'headers': self.headers, 'timeout': 30}
        response=Request.basic(options)
        if response:
            if response.status_code==200:
                results_dict=json.loads(response.content)
                if results_dict['success']==True:
                    self.Parsecall(results_dict,dict_param['mon'])
                    return return_result(code=2000, data=None, desc=u"通话记录首次请求成功!!!")

                elif results_dict['success']==False:
                    return return_result(code=4610, data=None,
                                         desc=u"短信验证码错误!!!")
            else:
                return return_result(code=4000, data=None, desc=u"{"
                                                      u"}用户通话记录首次请求失败!!!".format(self.phone_num))
        else:
            return return_result(code=4000, data=None, desc=u"{"
                                                              u"}用户通话记录首次请求失败!!!".format(
                self.phone_num))

#获取通话记录的另外请求
    def getphonemsgothermonth(self,dict_param):
        url="http://service.js.10086.cn/my/actionDispatcher.do"
        form_data={
        'reqUrl':'MY_QDCXQueryNew',
        'busiNum':'QDCX',
        'queryMonth':dict_param['mon'],
        'queryItem':'1',
        'qryPages':'1:1002:-1',
        'qryNo':'1',
        'operType':'3',
        'queryBeginTime':dict_param['fday'],
        'queryEndTime':dict_param['lday']

        }
        options = {'method': 'post', 'url': url, 'form': form_data,
                   'params': None, 'cookies': self.cookies, 'headers': self.headers, 'timeout': 30}
        response = Request.basic(options)
        if response:
            if response.status_code==200:
                results=json.loads(response.content)
                if results['success']==True:
                    self.Parsecall(results,dict_param['mon'])
                else:
                    msg_desc=u'{}月份的通话记录获取失败'.format(dict_param['mon'])
                    print msg_desc
                    return return_result(code=4000, data=None, desc=msg_desc)
            else:
                return return_result(code=4000, data=None, desc=u"{},"
                                                      u"{}月份的通话记录请求失败!!!".format(self.phone_num,dict_param['mon']))
        else:
            return return_result(code=4000, data=None, desc=u"{},"
                                                              u"{}月份的通话记录请求失败!!!".format(
                self.phone_num, dict_param['mon']))

    # 获取短信的请求
    def get_duanxin(self,dict_param):
        url = "http://service.js.10086.cn/my/actionDispatcher.do"
        form_data = {
                'reqUrl': 'MY_QDCXQueryNew',
                'busiNum': 'QDCX',
                'queryMonth': dict_param['mon'],
                'queryItem': '6',
                'qryPages': '6:1006:-1',
                'qryNo': '1',
                'operType': '3',
                'queryBeginTime':dict_param['fday'],
                'queryEndTime':dict_param['lday']
            }
        self.headers["Referer"] = "http://service.js.10086.cn/my/MY_QDCX.html"
        self.headers["Origin"] = "http://service.js.10086.cn"
        self.headers["Host"] = "service.js.10086.cn"

        options = {'method': 'post', 'url': url, 'form': form_data,
                       'params': None, 'cookies': self.cookies, 'headers': self.headers, 'timeout': 30}
        response = Request.basic(options)
        if response.status_code==200:
            results = json.loads(response.content)
            if results['success']==True:
                self.ParseNote(results,dict_param['mon'])
            else:
                msg_desc = u'{}月份的短信记录获取失败'.format(dict_param['mon'])
                print msg_desc
                return return_result(code=4000, data=None, desc=msg_desc)
        else:
            return return_result(code=4000, data=None, desc=u"{"
                                                  u"}月份的短信记录请求失败!!!".format(dict_param['mon']))

    #我的套餐数据请求
    def getMyproduct(self):
        productstr=''
        url="http://service.js.10086.cn/my/MY_WDYW.html"
        self.headers["Referer"]="http://service.js.10086.cn/my/MY_WDYW.html"
        self.headers["Host"]="service.js.10086.cn"
        options = {'method': 'post', 'url': url, 'form':None,
                   'params': None, 'cookies': self.cookies, 'headers': self.headers, 'timeout': 30}
        response=Request.basic(options)
        if response.status_code==200:
            bsoup = BeautifulSoup(response.content)

            script_results = bsoup.find_all("script")

            for i in range(8, len(script_results)):

                script_product = str(script_results[i])

                re_result = re.search(r'({.*})',script_product).group(1)

                json_result = json.loads(re_result)

                if 'resultObj' in json_result:
                    result_dict = json_result['resultObj']
                    #获取余额信息
                    if "accountBalance" in result_dict:
                        Crawlinfo.__user_dict['balance'] = json_result['resultObj']["accountBalance"]

                    if 'KEY_bizList' in result_dict:
                        result_list = json_result['resultObj']['KEY_bizList']
                        for i in range(len(result_list)):
                            productstr += result_list[i]["pkgName"] + ','
                        Crawlinfo.__user_dict['product_name'] =productstr[:-1]
            return return_result(code=2000, data=None, desc=u"获取用户套餐数据成功")
        else:
            return return_result(code=4000, data=None, desc=u"用户套餐数据请求失败.....")

    #获取基本信息前需要验证码的请求
    def getbasic_msgcode(self):
        url="http://service.js.10086.cn/my/sms.do"
        form_data = {
            "busiNum": "MY_GRZLGL_LOGIN"
        }
        self.headers["Referer"] = "http://service.js.10086.cn/my/MY_GRZLGL.html"
        self.headers["Origin"] = "http://service.js.10086.cn"
        self.headers["Host"] = "service.js.10086.cn"

        options = {'method': 'post', 'url': url, 'form': form_data,
                   'params': None, 'cookies': self.cookies, 'headers': self.headers, 'timeout': 30}
        response=Request.basic(options)
        if response.status_code==200:
            result=json.loads(response.content)
            if result['success']==True:
                return return_result(code=2000,data=None,desc=u"获取用户基本信息短信验证码成功!!!")
            else:
                return return_result(code=4000, data=None, desc=u"获取用户基本短信验证码请求失败!!!")
        else:
            return return_result(code=4000, data=None, desc=u"手机号为{}获取用户基本短信验证码请求失败!!!".format(self.phone_num))

    #获取用户基本信息的请求
    def get_basicInfo(self):
        import time
        timelist=[]
        #http://service.js.10086.cn/my/MY_GRZLGL.html
             #http://service.js.10086.cn/my/MY_GRZLGL.html
        url="http://service.js.10086.cn/my/MY_GRZLGL.html"
        self.headers["Referer"]="http://service.js.10086.cn/my/MY_GRZLGL.html"
        self.headers["Host"]="service.js.10086.cn"

        options = {'method': 'get', 'url': url, 'form':None,
                   'params': None, 'cookies': self.cookies, 'headers': self.headers, 'timeout': 30}
        response=Request.basic(options)
        if response.status_code==200:
            htmlresult=response.content
            # 获取基本信息
            bsoup=BeautifulSoup(response.content)
            script_result = bsoup.find_all("script")

            results = str(script_result[-3])

            re_result = re.search(r'({.*})', results).group(1)
            try:
                dict_result = json.loads(re_result)
                Crawlinfo.__user_dict['name'] = dict_result["resultObj"]['kehuName']
                # 手机号码
                Crawlinfo.__user_dict['phone'] = dict_result["resultObj"]["shoujihaoma"]
                # 用户状态
                Crawlinfo.__user_dict['user_valid'] = dict_result["resultObj"]["yonghuState"]
                # 入网时间
                timestr=dict_result["resultObj"]["ruwangAt"]
                timelist.append(timestr[:4])
                timelist.append(timestr[4:6])
                timelist.append(timestr[6:8])
                ruwangAt = '-'.join(timelist)
                Crawlinfo.__user_dict['open_date'] =ruwangAt
                # 客户星级
                Crawlinfo.__user_dict['level'] = dict_result["resultObj"]["kehuxingji"]
            except Exception as e:
                print  e
                return return_result(code=4000, data=None, desc=u"用户基本信息解析错误")

            #调用百度接口获取用户手机号归属定等信息
            phoneinfo=get_phone_attr(self.phone_num)
            if phoneinfo['code']==2000:
                Crawlinfo.__user_dict['province']=phoneinfo['data']['province']
                Crawlinfo.__user_dict['city']=phoneinfo['data']['city']
                Crawlinfo.__user_dict['company']=phoneinfo['data']['company']
            else:
                return phoneinfo
                Crawlinfo.__user_dict['cert_type']=''
                Crawlinfo.__user_dict['sex']=''
                Crawlinfo.__user_dict['address']=''
                Crawlinfo.__user_dict['cert_num']=''
            return return_result(code=2000,data=None,desc=u"获取用户基本信息成功")
        else:
            return return_result(code=4000, data=None, desc=u"{}用户基本信息请求失败".format(self.phone_num))

    #解析通话记录的方法
    @staticmethod
    def Parsecall(data_dict,mon):
        call_dict={}
        try:
            print "正在获取的通话记录日期为：",data_dict["resultObj"]['qryInterval']
            detail_list = data_dict["resultObj"]['qryResult']['gsmBillDetail']
            for i in range(1, len(detail_list)):
                call_dict["phone"] = detail_list[i]["user"]
                call_dict["call_area"] = detail_list[i]["visitArear"]
                call_dict["call_date"] = detail_list[i]["startTime"][:10]
                call_dict["call_time"] = detail_list[i]["startTime"][10:]
                call_dict["call_cost"] = detail_list[i]["feeItem01"]
                call_dict["call_long"] = detail_list[i]["callDuration"]
                call_dict["other_phone"] = detail_list[i]["otherParty"]

                #对呼叫类型进行分类数据有u'主叫本地'，u'主叫漫游'，u'被叫漫游'，u'被叫本地'
                if  detail_list[i]["statusType"]==u'主叫本地':
                    call_dict["call_type"] =1
                elif detail_list[i]["statusType"]==u'被叫本地':
                    call_dict["call_type"] = 2
                else:
                    call_dict["call_type"] = 3

                #对通话类型进行分类数据中有：u'本地(非漫游、被叫)'，u'国内长途',
                if u'本地' in detail_list[i]["roamType"]:
                    call_dict["land_type"]=1
                elif u'省内' in detail_list[i]["roamType"]:
                    call_dict["land_type"] = 2
                else:
                    call_dict["land_type"] = 3
                call_dict["cert_num"]=''
                Crawlinfo.__t_operator_call.append(call_dict)
                call_dict = {}
            Crawlinfo.__judge_clist.pop()
        except Exception as e:
            print e
            print u"当月{}无通话记录".format(mon)

#解析短信记录的方法
    @staticmethod
    def ParseNote(msg_dict,mon):
        note_dict = {}
        try:
            print "正在获取的短信数据时间段为：",msg_dict["resultObj"]["qryInterval"]
            msg_list = msg_dict["resultObj"]["qryResult"]["smsBillDetail"]
            for i in range(len(msg_list)):
                msg = msg_list[i]
                note_dict["business_type"] = u'短信'
                note_dict["note_time"] = msg["startTime"][10:]
                note_dict["phone"] = msg["user"]
                note_dict["other_phone"] = msg["otherParty"]
                note_dict["note_cost"] = msg["feeItem01"]
                note_dict["note_date"] = msg["startTime"][:10]
                note_dict["cernum"] = ''
                Crawlinfo.__t_operator_note.append(note_dict)
                note_dict = {}
            #解析完一个月份就从列表里剔除一个数据
            Crawlinfo.__judge_nlist.pop()
        except Exception as e:
            print e
            print u'{}当月无短信数据'.format(mon)

    #通过这个方法将最终获取的数据返回
    def getResult(self):
        Crawlinfo.__result_data['t_operator_user']=[Crawlinfo.__user_dict]
        Crawlinfo.__result_data['t_operator_call']=Crawlinfo.__t_operator_call
        Crawlinfo.__result_data['t_operator_note']=Crawlinfo.__t_operator_note

        #如果定义的两个列表都为空说明数据解析了6次对应6个月的数据都爬取了，否则数据不全
        if Crawlinfo.__judge_clist ==[] and Crawlinfo.__judge_nlist ==[]:
            return return_result(code=2000, data=Crawlinfo.__result_data,
                     desc=u"流程成功全部有数据!!!")
        else:
            return return_result(code=2001, data=Crawlinfo.__result_data,
                     desc=u"流程成功部分有数据!!!")

def controlCrawl(crawldata,msgcode):
    import time
    from copy import copy
    param_list = []
    param_dict = {}
    #通话记录与短信记录从当前月份开始的前6个月
    date_seq = getMonthSeq()
    for seq in date_seq:
        year = int(seq[:4])
        mon = int(seq[-2:])
        param_dict['mon']=seq
        param_dict['fday']=get_firstday_of_month(year, mon)
        param_dict['lday']=get_lastday_of_month(year, mon)
        param_list.append(param_dict)
        param_dict={}

    param_list.reverse()
    param_list2=copy(param_list)
    if isinstance(crawldata,Crawlinfo):
        #带上验证码获取第一个月份的数据
        result_dict=crawldata.getphonemsgfirst(msgcode,param_list.pop())
        if result_dict['code']==2000:
            for i in range(len(param_list)):
                try:
                    crawldata.getphonemsgothermonth(param_list.pop())
                except Exception as e:
                    print e
                    continue

            for i in range(len(param_list2)):
                try:
                    crawldata.get_duanxin(param_list2.pop())
                except Exception as e:
                    print e
                    continue
        else:
            return result_dict

        if result_dict['code']==2000:
            try:
                result_dict=crawldata.getMyproduct()
                if result_dict['code']==2000:
                    print "套餐数据获取成功"
                else:
                    print result_dict

                result_dict=crawldata.get_basicInfo()
                if result_dict['code']==2000:
                    print "用户基本信息获取成功"
                else:
                    print result_dict
            finally:
                return crawldata.getResult()
        else:
            return result_dict

def login_crawl_js(**kwargs):
    spiderjs=ChinaMobile_JS(kwargs.get("phone_num"),kwargs.get("password"))
    result_dict=spiderjs.LoingVsy()
    if result_dict["code"]==2000:
        print "登录成功，开始获取短信验证码"
        result_dict=spiderjs.getmsgcode()
        return result_dict
    else:
        return result_dict

#登录并获取验证码后，用手机号与cookie实例化爬虫类再用验证码作为参数调用相关爬虫去获取数据
def spiderApi(**kwargs):
    import ast
    #判断cookies格式的合法性必须是字典才行
    cookies_dict=kwargs.get('cookies')
    if isinstance(cookies_dict,str):
        #将字典形式的字符串转成字典
        cookies = ast.literal_eval(cookies_dict)
        crawldata=Crawlinfo(kwargs.get("phone_num"),cookies)
        return controlCrawl(crawldata,kwargs.get('code'))

    elif isinstance(cookies_dict,dict):
        crawldata = Crawlinfo(kwargs.get("phone_num"), cookies_dict)
        return controlCrawl(crawldata, kwargs.get('code'))

if __name__=="__main__":
    d={"phone_num":"15152224741","password":"921724"}
    cookies=login_crawl_js(**d)['data']
    print cookies
   # cookies={'CmWebtokenid': '15152224741,js', 'smsMobile': '15152224741-D734611756AB4B137575AF64E7C70E0E', 'JSESSIONID': 'wvnXZl9fLMfhZ2hbvvDSn92m7RrvwGP2QJvzJmQr30KqPRhQLRGw!1929226179', '15152224741_smsVerifyCode': 'A5F2FC429B5AFAFF9F9049BA27315A09B73623CBE1E8FE90', 'AlteonP': 'AgfxGWddqMAo5qEx1AafVQ$$', 'last_success_login_mobile': '15152224741', 'cmtokenid': '7000885E43FA4A99A46320D595076395@js.ac.10086.cn'}
    code=raw_input("please input msgcode:")
    s={'phone_num':"15152224741",'cookies':cookies,'code':code}
    spiderApi(**s)






















