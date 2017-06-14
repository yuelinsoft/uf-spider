#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import pdb
import os,time
import json
from desc_code import returnResult,current_milli_time
from alipay_count import getPhonelist
from public import Request

import requests
try:
    import urllib2,urllib
    import traceback
    import requests,re
    from requests.utils import dict_from_cookiejar
    from bs4 import BeautifulSoup
    from selenium.webdriver.support.wait import WebDriverWait
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.by import By
except Exception,e:
    print u"模块加载失败"
    print e
    os._exit(0)



# 如果登录界面没有加载成功，可以加载10次
class Alipay(object):
    """
    test:username:'18188600687'
        password:'LJS123'

    """

    def __init__(self,username,password):
        self.username=username
        self.password=password
        self.url='https://auth.alipay.com/login/index.htm'

    def visitAlipay(self):
        global browser
        #browser=webdriver.Chrome()
        # 使用无头浏览器
        browser = webdriver.PhantomJS(executable_path='D:/phantomjs-2.1.1-windows/bin/phantomjs')
        # 将浏览器最大化
        browser.maximize_window()
        # 打开支付宝登录界面
        browser.get(url=self.url)
        # 设置等待时间等页面加载过来了再查找元素
        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "J-loginMethod-tabs"))
            )
        except:
            print "登录页面加载异常........"
        a=False
        t = 0
        while t < 10:
            print "start ......."
            try:
                # 用户名
                browser.find_element_by_id('J-input-user')
                # 密码
                browser.find_element_by_id('password_rsainput')
                # 登录按钮
                browser.find_element_by_id('J-login-btn')
                a=True
                print "start visit loginpage"
                break
            except:
                time.sleep(2)
                t+=1
        if a == True:
                #页面加载成功调用登录的方法，退出循环
            return self.login(browser,self.username,self.password)
        else:
            print "登录页面加载10次后仍旧异常退出程序......."
            return dict(code=4200)

    def login(self,browser, user, password):
        """
        在上面页面加载正常元素定位清楚后进行登录
        :param user:
        :param password:
        :return:
        """
        try:
            browser.find_element_by_id('J-input-user').click()
            browser.find_element_by_id('J-input-user').clear()
            browser.find_element_by_id('J-input-user').send_keys(user)
            browser.find_element_by_id('password_rsainput').click()
            browser.find_element_by_id('password_rsainput').clear()
            browser.find_element_by_id('password_rsainput').send_keys(password)
            #如果有验证码这里需要增加破解验证码的代码
            # 不需要验证码的情况，直接点击登录
            browser.find_element_by_id('J-login-btn').click()
        except:
            return dict(code=2100)

           #判断是否需要短信验证码

        try:
            element = WebDriverWait(browser,3).until(
                EC.presence_of_element_located((By.CLASS_NAME, "ui-tiptext-content"))
                )
            return self.get_Login_msgcode(browser)
        except:
            print "不需要短信验证码"

        try:
            element = WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.ID, "globalUser"))
            )
            return self.visitMyalipay()
        except:
            return dict(code=4000)

    def get_Login_msgcode(self,browser):
        msg_code=raw_input("请输入您收到的短信验证码：")
        msg_code=msg_code.strip()
        time.sleep(5)
        t=0
        a=False
        while a<5:
            try:
                browser.find_element_by_id("riskackcode")
                browser.find_element_by_xpath('//*[@id="J-submit"]/input')
                a=True
                break
            except:
                t+=1
        if a==True:
            browser.find_element_by_id("riskackcode").click()
            browser.find_element_by_id("riskackcode").clear()
            browser.find_element_by_id("riskackcode").send_keys(msg_code)
            # 点击下一步操作
            browser.find_element_by_xpath('//*[@id="J-submit"]/input').click()
            time.sleep(3)
            # 点击完后访问我的支付宝
            return self.visitMyalipay()
        else:
            print "短信验证码元素定位失败退出程序"
            return dict(code=4400)

    def visitMyalipay(self):
        print u"点击我的支付宝"
        t=0
        while t<5:
            try:
                if browser.find_element_by_xpath('//a[@seed="global-portal-v1"]'):
                    browser.find_element_by_xpath('//a[@seed="global-portal-v1"]').click()
                    time.sleep(2)
                    print u"第二步：点击我的支付宝成功"
                    break
                else:
                    print u"我的支付宝定位失败。。。"
            except:
                print u'点击我的支付宝失败，将每隔5秒尝试最多5次点击。'
                browser.refresh()
                time.sleep(2)
                t+=1
        if t==5:
            print u'最终在点击我的支付宝时失败，退出程序……'
            return dict(code=4000)
        all_handles = browser.window_handles
        browser.switch_to_window(all_handles[-1])
        #定位转账元素
        element = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="J-assets-balance"]/div[1]/div/div[2]/ul/li[3]/a'))
        )
        if element:
            return self.transFer()
    def transFer(self):
        print u'点击转账'
        #点击转账到支付宝转账页面
        t=0
        a=False
        while t<5:
            try:
                if browser.find_element_by_xpath('//*[@id="J-assets-balance"]/div[1]/div/div[2]/ul/li[3]/a'):
                    browser.find_element_by_xpath('//*[@id="J-assets-balance"]/div[1]/div/div[2]/ul/li[3]/a').click()
                    time.sleep(3)
                    # 关闭没有用的窗口
                    all_handles = browser.window_handles
                    for handle in all_handles[:-1]:
                        browser.switch_to_window(handle)
                        browser.close()
                    # 关闭完后，切换回需要的窗口
                    browser.switch_to_window(all_handles[-1])
                    #定位输入手机号文本框元素
                    element = WebDriverWait(browser, 3).until(
                    EC.presence_of_element_located((By.ID, "ipt-search-key"))
                        )
                    if element:
                        a=True
                        print "跳转到转账页面成功！！！"
                        break
            except:
                print u'点击我的转账失败，将每隔5秒尝试最多5次点击。'
                browser.refresh()
                t += 1
        if a==True:
            return browser
        if t == 5:
            print u'最终在点击我的支付宝时失败，退出程序……'
            return dict(code=4000)

class check(object):
    def __init__(self,browser1):
        self.browser=browser1
        self.cookiestr = self.browser.get_cookies()

    #查询接口
    def checkAPI(self,phone_list):
        #pdb.set_trace()
        print u"开始查询"
        """
        输入手机号，返回查询的结果
        :param browser: 浏览器对象
        :param account: 需要检查的手机号
        :param jsonp: 这个是寻找返回值链接的一部分，需分析网页才能直到规律（初始值jsonp2后缀累加1）
        :return: 手机号对应的用户名字
        """
        # 输入手机号码
        #在这里输入手机号码对手机号码进行查询
        #对phone_list进行处理
        k=2
        for i in range(len(phone_list)):
            for key in phone_list[i]:
                if str(phone_list[i][key]).isdigit() and len(str(phone_list[i][key]))==11:
                    jsonp = 'jsonp' + str(k)
                    check_phone=str(phone_list[i][key]).strip()
                    check_name=self.search_phone(check_phone,jsonp)
                    if check_name:
                        check_name=str(check_name).strip()[1:].decode("utf-8")
                        phone_list[i]["check_name"]=check_name
                    else:
                        phone_list[i]["check_name"] = None
                    k+=1
        return phone_list

    #输入指定的手机号码进行搜索
    def search_phone(self,phone,jsonp):
        return_result=[]
        item={}
        t1 = current_milli_time()
        # 点击输入手机号的文本框，向文本框里输入手机号
        t=0
        a=False
        while t<5:
            try:
                if self.browser.find_element_by_id("ipt-search-key"):
                    self.browser.find_element_by_id("ipt-search-key").click()
                    self.browser.find_element_by_id("ipt-search-key").clear()
                    self.browser.find_element_by_id("ipt-search-key").send_keys(phone)
                    a=True
                    time.sleep(2)
                    break
            except:
                t+=1
                print "定位手机号文本框失败,尝试定位5次"
        if t==5:
            print "最终在定位手机号的文本框中失败,退出程序"
            return dict(code=4100)

            # 点击"校验收款人姓名"按钮
        if a==True:
            t=0
            while t<5:
                try:
                    if self.browser.find_element_by_id('receiveNameAlert'):
                        self.browser.find_element_by_id('receiveNameAlert').click()
                        time.sleep(3)
                        break
                except:
                    t+=1
                    print "最终在定位校验收款人的姓名时定位元素失败尝试5次"
            if t==5:
                return dict(code=4444)

        html = self.browser.page_source
        # 获取登录的信息
        soup = BeautifulSoup(html, 'lxml')
        hurl = soup.find('script', {'id': jsonp})['src']
        # 根据获取到的url发送请求获取用户数据
        if '443' in hurl:
            hurl=hurl.replace(':443','')
        else:
            hurl=hurl
        user_info = self.getHtml(hurl)
            #对用户数据进行处理
        try:
            result=str(user_info).decode('GBK')
            str2 = result.split(jsonp)[1]
            str3 = str2.split('(')[1].split(')')[0]
            alipay_dict = json.loads(str3)
        except:
            print "该用户的信息异常"
        try:
            check_name = alipay_dict['userInfo']['realname']
        except:
            check_name=None
        return check_name

    def getHtml(self,url,num_retries=2):
        url2=url
        cookies={}
        for cookie_dict in self.browser.get_cookies():
            cookies[cookie_dict['name']] = cookie_dict['value']
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Host':'shenghuo.alipay.com',
            'Referer':'https://shenghuo.alipay.com/send/payment/fill.htm?_pdType=adbhajcaccgejhgdaeih',
        }
        options = {'method': 'get', 'url': url2, 'form':None, 'params': None,
                   'cookies':cookies, 'headers':headers}
        response=Request.basic(options)
        if response:
            text=response.content
            print "get result success..."
        return text

def login_for_crawler():
    username = 'm15112643691@163.com'
    password = 'LYD123'
    ali = Alipay(username, password)
    return ali.visitAlipay()

def start(**kwargs):
    data = kwargs.get('data')
    msg_no=kwargs.get("msg_no")
    phone_list=getPhonelist(data)
    for p in phone_list:
        p["msg_no"]=msg_no
    #调用登录的函数进行登录
    browser=login_for_crawler()
    #对browser进行判断
    if type(browser)==dict:
        data=browser
        return returnResult(code=data["code"],data=None)
    else:
        c = check(browser)
        result_data = c.checkAPI(phone_list)
        return returnResult(2000, result_data)


if __name__=="__main__":
    """
    最终获得的用户数据有三种情况
    1.用户实名认证显示名字与号码无相关信息出来
    2.用户没有注册
    3.用户信息不完整。能显示名字。
    """

    d={
        "msg_no": "1",
        "data": {
            "name": u"张国玉",
            "id_num": "123456789",
            "phone1": "15626952003",
            "phone2": "null",
            "phone3": "13316593483",
            "company": u"联金所",
            "company_phone1": "123456789(1)",
            "company_phone2": "123456789(2)",
            "company_phone3": "123456789(3)",
            "company_address": u"福田XXX",
            "company_city": u"广东省深圳市",
            "spouse_name": u"郭俊锴",
            "spouse_id_card": "123456789",
            "spouse_phone1": "18580865372",
            "spouse_phone2": "null",
            "spouse_company": u"重庆长安汽车股份有限公司",
            "address": u"福田",
            "contact_name1": u"罗美婵",
            "contact_relationship1": u"朋友",
            "contact_phone1": "13903011645",
            "contact_name2": u"武学平",
            "contact_relationship2": u"朋友",
            "contact_phone2": "18976585566",
            "contact_name3": u"刘燕妮",
            "contact_relationship3": u"朋友",
            "contact_phone3": "18776111166",
            "contact_name4": u"戴盛生",
            "contact_relationship4": u"朋友",
            "contact_phone4": "13801918367",
            "contact_name5": u"农春影",
            "contact_relationship5": u"朋友",
            "contact_phone5": "13878833360",
            "contact_name6": u"刘家灯",
            "contact_relationship6": u"朋友",
            "contact_phone6": "13825037381",
            "contact_name7": u"张国玉",
            "contact_relationship7": u"朋友",
            "contact_phone7": "15626952003",
            "contact_name8": u"廖敬城",
            "contact_relationship8": u"朋友",
            "contact_phone8": "13760454549",
        }
    }

    start(**d)

