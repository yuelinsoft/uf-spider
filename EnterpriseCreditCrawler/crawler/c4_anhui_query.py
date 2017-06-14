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
    main_url='http://www.ahcredit.gov.cn/'
    headers_info_0={
        'Host':'www.ahcredit.gov.cn',
        # 'Proxy-Connection':'keep-alive',
        'Referer':'http://www.ahcredit.gov.cn/',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    }
    resp= requests.get(url=main_url,headers=headers_info_0,timeout = 10)#,allow_redirects=True)
    # print resp.requests.cookies
    main_url='http://www.ahcredit.gov.cn/'
    resp = requests.get(url=main_url, headers=headers_info_0, timeout=10, cookies=resp.cookies)#, allow_redirects=False)
    print resp.request.cookies
    cookies_code=dict(main_html.cookies)
    print 1111,cookies_code
    return cookies_code


def get_image(cookies):
    url = 'http://www.ahcredit.gov.cn/validateCode.jspx?type=1&id=0.33192827721152085'
    headers_info_2 = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Cache-Control':'max-age=0',
        'Host': 'www.ahcredit.gov.cn',
        'Referer':'http://www.ahcredit.gov.cn/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests':'1'
    }
    params_info_1={
        'type':'1',
        'id':''
    }
    CImages_html=Session.get(url=url,headers=headers_info_2,params=params_info_1,cookies=cookies,timeout = 10)
    file  = BytesIO(CImages_html.content)
    im = Image.open(file)
    return im

def get_html(name,string,cookies):
    check_url='http://www.ahcredit.gov.cn/checkCheckNo.jspx'
    headers_info_3 = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Host': 'www.ahcredit.gov.cn',
        'Origin':'http://www.ahcredit.gov.cn',
        'Referer':'http://www.ahcredit.gov.cn/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }
    checkNo= string
    data_info={
        'checkNo':checkNo
    }
    Session.post(url=check_url,headers=headers_info_3,data=data_info,cookies=cookies,timeout = 10)
    search_list='http://www.ahcredit.gov.cn/searchList.jspx'
    headers_info_4 = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Host': 'www.ahcredit.gov.cn',
        'Origin':'http://www.ahcredit.gov.cn',
        'Referer':'http://www.ahcredit.gov.cn/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }
    data_info_2={
        'checkNo' : checkNo,
        'entName' : name
    }
    search_html=Session.post(url=search_list,headers=headers_info_4,data=data_info_2,timeout = 10)
    content = search_html.content
    return content

def main(name):
    cookies = get_cookies()
    cookies = {}
    im = get_image(cookies)
    string = CheckCode.get_string(im)
    listPage = get_html(name,string,cookies)
    result_list = common.parse_url(listPage, 'li','font16','li','width:95%')
    if result_list == None:
        return main(name)
    else:
        return result_list


name = '融金所'
print main(name)