#coding=utf-8
import time
import requests
from requests.utils import dict_from_cookiejar
from lxml import etree
from io import BytesIO
from PIL import Image
from pytesseract import image_to_string
import os
import sys
from claw_report import controlSpider

from public import (
    Request,
    getIP,
    returnResult,
    getUserAgent,
    image_to_string,
    dict_from_cookiejar
)
reload(sys)
sys.setdefaultencoding("utf-8")

#忽略warnings的信息的代码
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

_cur_dir=os.path.dirname(__file__)

class CreditReport(object):
    #基本信息的设置
    def __init__(self,name,password,auth_code):
        self.headers = {
            'Referer': None,
            #'X-Forwarded-For': getIp(),
            'Accept-Language': 'zh-CN',
            'Connection': 'keep-alive',
            'Host': 'ipcrs.pbccrc.org.cn',
            'Accept-Encoding': 'gzip, deflate',
            'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'
        }
        self.threshold=10
        self.cookies=None
        self.host='https://ipcrs.pbccrc.org.cn'#主机地址
        self.name=name
        self.password=password
        self.auth_code=auth_code
        #认证信息
        self.auth_info=dict(
            user_name=self.name,
            password=self.password,
            id_code=self.auth_code
        )

        #开始发请求
        #访问主页
    def visitSys(self):
        url='https://ipcrs.pbccrc.org.cn/'
        options = {'method': 'get', 'url': url, 'form': None,
                   'params': None, 'cookies': None, 'headers': self.headers}
        response=Request.basic(options)
        if response:
            self.cookies = dict_from_cookiejar(response.cookies)
            # 下一步调用访问登录页面的方法
            return self.visitLoginpage()
        else:
            return dict(resutl=4000,error='visitSys function error')
        #end

    def visitLoginpage(self):
        url='https://ipcrs.pbccrc.org.cn/login.do?method=initLogin'
        self.headers['Referer']='https://ipcrs.pbccrc.org.cn/top1.do'
        options = {'method': 'get', 'url': url, 'form': None, 'params': None,
                   'cookies': self.cookies, 'headers': self.headers}
        response=Request.basic(options)
        #如果请求成功就发起登录请求
        if response:
            #print "success"
            #在登录页面里获取登录所需要的信息，以字典保存下来
            path_dict=dict(date='//input[@name="date"]/@value',
                           code_url='//img[@id="imgrc"]/@src',#验证码的url
                           token='//input[@name="org.apache.struts.taglib.html.TOKEN"]/@value' )
            #根据路径调用抽取数据的方法
            result=self.xpathText(response.text,path_dict)
            #根据获取到的验证码图片的url获取验证码
            if result['date'] and result['code_url'] and result['token']:
                code=self.getCode(self.host+result['code_url'])
                form_item=dict(token=result['token'],date=result['date'],code=code)

                #获得参数后调用登录的方法
                return self.loginSys(form_item)
            else:
                return dict(result=4100,error='xpath not found')
        else:
            return dict(result=4000,error='visitLoginpage function')
    # #end

    def xpathText(self,response_text,path_dict):
        if not isinstance(path_dict,dict):
            raise ValueError(u'')
        else:
            keys=path_dict.keys()
            #将数据以字典的形式保存下,默认value为False
            result_dict=dict(zip(keys,[False]*len(keys)))
            selector=etree.HTML(response_text)
            for key,value in path_dict.iteritems():
                try:
                    result_dict[key]=selector.xpath(value)[0].strip()
                except IndexError:
                    pass
            return result_dict

    #登录的请求,获得参数后正式传参
    def loginSys(self,form_item):
        #print form_item
        form={
            'org.apache.struts.taglib.html.TOKEN':'7f0a9fd773858af21f9b68a31286b086',
            'method':'login',
            'date':'1479264399675',
            'loginname':'liuyading',
            'password':'python8899',
            '_@IMGRC@_':'gyvsep'

        }
        form['date']=form_item['date']
        form['_@IMGRC@_']=form_item['code']#验证码
        form['password']=self.auth_info['password']#密码
        form['loginname']=self.auth_info['user_name']#用户名
        form['org.apache.struts.taglib.html.TOKEN']=form_item['token']
        url='https://ipcrs.pbccrc.org.cn/login.do'
        self.headers['Referer']='https://ipcrs.pbccrc.org.cn/page/login/loginreg.jsp'

        options = {'method': 'post', 'url': url, 'form': form, 'params': None,
                   'cookies': self.cookies, 'headers': self.headers}

        response=Request.basic(options)
        #如果请求成功回到欢迎页面
        if response:
            error=self.loginError(response.text)
            if error['error']==None:
                return self.welcomePage()
            #验证码错误从新去获取验证码
            elif error['error']=='code':
                if self.threshold>0:
                    self.threshold-=1
                    form_item['code']=self.updateCode()
                    return self.loginSys(form_item)
                else:
                    return dict(result=4200,error='image recognition failed')
            elif error['error']=='user_name':
                return dict(result=4600,error='user_name or pw error')
        else:
            return dict(result=4000,error='loginByJS function')


    def loginError(self,text):
        selector=etree.HTML(text)
        error=selector.xpath('//div[@class="erro_div3"]')
        if len(error)==1:
            if error[0].xpath('//span[@id="_@MSG@_"]/text()'):#验证码错误的信息
                return dict(error='code')
            elif error[0].xpath('//span[@id="_error_field_"]/text()'):#密码或者用户名错误
                return dict(error='user_name')
        else:
            return dict(error=None)

#欢迎页面
    def welcomePage(self):
        url='https://ipcrs.pbccrc.org.cn/welcome.do'
        self.headers['Referer']='https://ipcrs.pbccrc.org.cn/login.do'

        options = {'method': 'get', 'url': url, 'form': None, 'params': None,
                   'cookies': self.cookies, 'headers': self.headers}
        response=Request.basic(options)
        #如果能请求到欢迎页面就调用输入身份验证码的方法
        if response:
            text=response.content
            #filename='welcome.html'
            return self.inputIdcode()
        else:
            return dict(result=4000,error='welcomePage function')

    #识别验证码的方法
    @staticmethod
    def recogImage(content):
        file=BytesIO(content)
        img=Image.open(file)
        img=(img.convert('L')).resize((200,65))
        result=image_to_string(img).strip()
        result=result if result.isalnum() else False
        img.close()
        file.close()
        return result

    #end
    #获取验证码的方法
    def getCode(self,url,save_path='./code'):
        options = {'method': 'get', 'url': url, 'form': None, 'stream': True,
                   'cookies': self.cookies, 'headers': self.headers}
        response=Request.basic(options)

        if response:
            #print "get Code requests success"
            return self.recogImage(response.content)
        else:
            return dict(result=4000,error='getNoteCode function')

    #当验证码识别错误时调用这个方法
    def updateCode(self,save_path='./code'):
        #获得毫秒级的时间戳作为验证码url的参数
        current_milli_time = lambda: int(round(time.time() * 1000))
        url='https://ipcrs.pbccrc.org.cn/imgrc.do?a='+str(current_milli_time())
        options = {'method': 'get', 'url': url, 'form': None, 'stream': True,
                   'cookies': self.cookies, 'headers': self.headers}
        response=Request.basic(options)

        if response:
            return self.recogImage(response.content)
        else:
            return dict(result=4000,error='updateCode function')


    #输入身份验证的方法
    def inputIdcode(self):
        form={
            'method':'checkTradeCode',
            'code':'kyp4yi',
            'reportformat':'21'
        }
        form['code']=self.auth_info['id_code']
        url='https://ipcrs.pbccrc.org.cn/reportAction.do'
        self.headers['Referer']='https://ipcrs.pbccrc.org.cn/reportAction.do?method=queryReport'
        options = {'method': 'post', 'url': url, 'form': form, 'params': None,
                   'cookies': self.cookies, 'headers': self.headers}
        response=Request.basic(options)
        #如果请求成功，获取最终的源代码，也就是调用获取源代码的方法
        if response:
            #没有返回内容
            if (response.text).strip()==str(0):
                return self.acquireReport()
            else:
                return dict(result=4444,error="auth_code error")
        else:
            return dict(result=4000,error='inputIdcode function error')
    #end


    def acquireReport(self):
        url="https://ipcrs.pbccrc.org.cn/simpleReport.do?method=viewReport"
        form={
            'tradeCode': 'kyp4yi',
            'reportformat':21
        }
        form['tradeCode'] = self.auth_info['id_code']
        self.headers['Referer'] = 'https://ipcrs.pbccrc.org.cn/reportAction.do?method=queryReport'

        options = {'method': 'post', 'url': url, 'form': form, 'params': None,
                   'cookies': self.cookies, 'headers': self.headers}
        response=Request.basic(options)
        if response:
            file_name=self.auth_info['user_name']+'.html'

            #调用保存页面的函数,当页面保存成功时返回字典result值为2000
            file_name2=self.saveHtml(response.text,file_name)
            if file_name2:
                return dict(result=2000,file_name=file_name2)
            else:
                raise ValueError(u'保存错误')

            # if self.saveHtml(response.text,file_name)==True:
            #     return dict(result=2000,file_name=file_name)
            # else:
            #     raise ValueError(u'保存错误')
        else:
            return dict(result=4000,error='acquireReport function')

    #保存页面的方法
    def saveHtml(self,text,file_name):
        #获得函数当前工作的路径
        path_save=os.path.join(_cur_dir,'templates')
        if not os.path.exists(path_save):
            os.makedirs(path_save)
        file_name2=os.path.join(path_save,file_name)
        with open(file_name2,'w') as f:
            f.write(text)
        return file_name2

def debugTest(name,password,auth_pwd,filename=None):
    #调试模式
    data=controlSpider(filename)
    return data

def creditReportAPI(name,password,auth_pwd,debug=True):
    """
    实现接口，当debug为True时解析本地的测试html返回结果
    :param name: 用户名
    :param password: 登录密码
    :param auth_pwd: 身份验证码
    :param debug:
    :return: dict(person = 字典列表, card = 字典列表, query = 字典列表)
    """
    name=name.strip()
    password=password.strip()
    auth_pwd=auth_pwd.strip()

    person=CreditReport(name,password,auth_pwd)
    #要是流程成功最终保存用户的征信报告以html的格式
    #最终会返回一个字典给result
    result=person.visitSys()
    if result['result']==2000:
        html_name=result['file_name']

        #如果要对页面进行解析则设置debug=True
        if debug == True:
            result= debugTest(name, password, auth_pwd,filename=html_name)

        return returnResult(code=2000,data=result)
    else:
        return returnResult(code=result['result'],data={})

if __name__=="__main__":
    creditReportAPI('ql2614', 'qujing1129', 'gg7n3c')

