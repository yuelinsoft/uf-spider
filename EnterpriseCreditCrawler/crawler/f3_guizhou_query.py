#coding=utf-8
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.slide_check_code_recognition import get_validate_data_based_offline
import json
import requests
from requests.utils import dict_from_cookiejar
from EnterpriseCreditCrawler.common import url_requests
from requests import cookies
Session=requests.Session()
import pdb


#得到challenge
class GuiZhouQuery(object):
    def __init__(self):
        self.headers={
        'Host':'gz.gsxt.gov.cn',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Referer':'http://gz.gsxt.gov.cn/',
        'Origin':'http://gz.gsxt.gov.cn'
    }
        self.cookies=None
    def get_cookies(self):
        url = "http://gz.gsxt.gov.cn/2016/images/search-su.png"
        self.headers['Host'] = 'gz.gsxt.gov.cn'
        self.headers['Referer'] = 'http://gz.gsxt.gov.cn/list.jsp'
        response = url_requests.post(url=url, headers=self.headers,proxies=proxies)
        if response.status_code == 200:
            cookies = dict_from_cookiejar(response.cookies)
            self.cookies = cookies
            return self.get_Captchal()
        elif response.status_code == 502:
            return self.get_cookies()

    def get_Captchal(self):
        url="http://gz.gsxt.gov.cn/query!StartCaptcha.shtml"
        response=url_requests.get(url=url,headers=self.headers,cookies=self.cookies,proxies=proxies)
        if response.status_code==200:
            data=response.content
            data=json.loads(data)
            challenge=data.get('challenge')
            cookies=dict_from_cookiejar(response.cookies)
            print "shtml.cookies:",cookies
            return  challenge,cookies
        elif response.status_code==502:
            return self.get_Captchal()

    def update_cookies(self,cookies):
        ## http://gz.gsxt.gov.cn/search!pv.shtml
        url="http://gz.gsxt.gov.cn/search!pv.shtml"
        form_data={
            "sys":"1",
            "pg":"http://gz.gsxt.gov.cn/list.jsp",
            "rf":"http://gz.gsxt.gov.cn/list.jsp"
        }
        headers = {
            'Host': 'gsxt.gzgs.gov.cn',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
            'Referer': 'http://gz.gsxt.gov.cn/list.jsp',
            'Origin':'http://gz.gsxt.gov.cn'
        }
        response=url_requests.post(url=url,headers=headers,data=form_data,cookies=cookies,proxies=proxies)
        if response.status_code==200:
            cookies=dict_from_cookiejar(response.cookies)
           # print "update.cookies:",cookies
            return cookies
        elif response.status_code==502:
            return self.update_cookies(cookies)

#验证码认证通过后根据输入的企业名称得到页面结果
def getresult(geetest_data,company_name,cookies):
    url="http://gz.gsxt.gov.cn/query!searchSczt.shtml"
    geetest_data['q']=company_name
    headers={
        'Host': 'gz.gsxt.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36',
        'Referer':'http://gsxt.gzgs.gov.cn/list.jsp',
        'Origin':'http://gz.gsxt.gov.cn'
    }
    response=url_requests.post(url=url,data=geetest_data,headers=headers,cookies=cookies,proxies=proxies)
    if response.status_code==200:
        html=response.content
        return html
    elif response.status_code==502:
        return getresult(geetest_data,company_name,cookies)

def append_list(jsonA,cookies):

    url_list=[]
    info=jsonA['data']
    if info !=[]:
        for i in info:
            detail_list = []
            company_dict={}
            tag_nbxh=i["nbxh"] #对应下一个页面请求的参数
            tag_ztlx=i["ztlx"] #2
            tag_qymc=i["qymc"] #查询出的公司名字
            company_dict['company']=tag_qymc
            detail_list.insert(0,tag_nbxh)
            detail_list.insert(1,cookies)
            company_dict['detail']=detail_list
            tag_zch=i["zch"]   #公司注册号
            url_list.append(company_dict)
    return url_list

def main(**kwargs):
    global proxies
    proxies=kwargs.get('proxies')
    company=kwargs.get('name')
    # #得到初始的cookies
    g=GuiZhouQuery()
    challenge, cookies=g.get_cookies()
    #print cookies
    geetest_data=get_validate_data_based_offline(challenge)
    cookies2=g.update_cookies(cookies)
    cookies['SERVERID']=cookies2['SERVERID']
    #cookies=g.Visit_list(geetest_data,company,cookies)
    cookies['UM_distinctid'] = '15bfb72d13ca9b-0d2c7185935fa7-4e47052e-1fa400-15bfb72d13d25'
    cookies['CNZZDATA2123887'] = 'cnzz_eid%3D878425714-1494572259-http%253A%252F%252Fgz.gsxt.gov.cn%252F%26ntime%3D1494572259'
    result = getresult(geetest_data, company, cookies)
    dict_result = json.loads(result)
    if dict_result["successed"] == True:
        print "验证码认证成功"
        # 获取需要的数据
        result_list = append_list(dict_result,cookies)
        return result_list

if __name__=="__main__":
    #test_proxies()
   print main(name="贵州金伟莲贸易有限公司",proxies=None)
