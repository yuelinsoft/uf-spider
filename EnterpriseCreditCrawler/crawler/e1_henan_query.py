#-*- coding:utf-8 -*-
# author: 'KEXH'
from common import conf,common,CheckCode
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import requests
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO
from PIL import Image
Session=requests.Session()

#拿cookies
def get_cookies():
    # try:
    main_url='http://www.ahcredit.gov.cn/search.jspx'
    headers_info_0={
        'Host':'www.ahcredit.gov.cn',
        'Proxy-Connection':'keep-alive',
        'Referer':'http://gsxt.saic.gov.cn/',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    }
    main_html=Session.get(url=main_url,headers=headers_info_0,timeout = 10)
    cookies_code=dict(main_html.cookies)
    return cookies_code


def get_image(cookies):
    url = 'http://222.143.24.157/validateCode.jspx?'
    headers_info_2 = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Host': '222.143.24.157',
        'Referer':'http://222.143.24.157/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Connection': 'keep-alive'
    }
    params_info_1={
        'type':'1',
        'id':''
    }
    CImages_html=Session.get(url=url,headers=headers_info_2,params=params_info_1,timeout = 10)
    file  = BytesIO(CImages_html.content)
    im = Image.open(file)
    return im

def get_html(name,string,cookies):
    check_url='http://222.143.24.157/checkCheckNo.jspx'
    headers_info_3 = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Host': '222.143.24.157',
        'Referer':'http://222.143.24.157/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Connection': 'keep-alive'
    }
    checkNo= string
    data_info={
        'checkNo':checkNo
    }
    Session.post(url=check_url,headers=headers_info_3,data=data_info,timeout = 10)
    search_list='http://222.143.24.157/searchList.jspx'
    headers_info_4 = {
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Host': '222.143.24.157',
        'Referer':'http://222.143.24.157/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    }
    data_info_2={
        'checkNo' : checkNo,
        'entName' : name
    }
    search_html=Session.post(url=search_list,headers=headers_info_4,data=data_info_2,timeout = 10)
    content = search_html.content
    return content

def main(name):
    cookies = {'clwz_blc_pst_DMZ_xb8xbaxd4xd8xbexf9xbaxe2x3a9090': '690006208.34083', 'JSESSIONID': '0000Zu9o-xAt6BXi9yKd3gcox6N:-1'}
    im = get_image(cookies)
    string = CheckCode.get_string(im)
    listPage = get_html(name,string,cookies)
    result_list = common.parse_url(listPage, 'li', 'font16', 'li', 'width:95%')
    if result_list == None:
        return main(name)
    else:
        return result_list

if __name__ == '__main__':
    name = '融金所'
    print main(name)