#-*- coding:utf-8 -*-
# author: 'KEXH'
from EnterpriseCreditCrawler.common import conf,captcha
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import requests
from operator import itemgetter
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO
from PIL import Image
import pytesseract
from bs4 import BeautifulSoup
Session=requests.Session()

def get_image():
    url = 'http://gsxt.cqgs.gov.cn/sc.action?width=130&height=40&fs=23'
    headers_info_2 = {
        'Accept' : 'image/png,image/*;q=0.8,*/*;q=0.5',
        'Accept-Encoding':'gzip, deflate',
        'Host': 'gsxt.cqgs.gov.cn',
        'Referer':'http://gsxt.cqgs.gov.cn/search_research.action',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Proxy-Connection': 'keep-alive',
    }
    CImages_html=Session.get(url=url,headers=headers_info_2,timeout = 10)
    file  = BytesIO(CImages_html.content)
    im = Image.open(file)
    return im


def get_stings(im):
    im = im.crop((0,0,60,40))
    # im.show()
    colors = im.getcolors()
    data_colors = sorted(colors, key = itemgetter(0),reverse=True)[1][1]
    w,h = im.size
    for y in range(h):
        for x in range(w):
            pixel = im.getpixel((x, y))
            if pixel != data_colors:
                im.putpixel((x, y), (255,255,255))
    try:
        string = pytesseract.image_to_string(im, lang='chi_sim',config ='-psm 7').strip()
        string = captcha.replaceStr(string)
        if '加' in string:
            answer = int(string[0]) + int(string[-1])
        else:
            answer = int(string[0]) - int(string[-1])
    except:
        answer = 'wrong'

    return answer


def get_html(company_name, string):
    url = 'http://gsxt.cqgs.gov.cn/search_research.action'
    headers_info = {
        'Accept-Encoding':'gzip, deflate',
        'Host': 'gsxt.cqgs.gov.cn',
        'Referer':'http://gsxt.cqgs.gov.cn/search.action',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Proxy-Connection': 'keep-alive'
    }
    data = {
        'code' : str(string),
        'key' :  company_name,
        'outSearch' :  '',
        'stype' : ''
    }
    req=Session.post(url=url,headers=headers_info,data=data,timeout = 10)
    content = req.text
    return content


def parse(html):
    soup = BeautifulSoup(html,'html.parser')
    info = soup.findAll(class_='name')
    url_list = []
    if info != None:
        for i in info:
            data_id = i['data-id']
            data_type = i['data-type']
            data_entId = i['data-entid']
            company_name = i.text.strip()
            url_list.append([data_entId,data_id,company_name,data_type])
    return url_list


def main(**kwargs):
    name = kwargs.get('name')
    global _proxies
    _proxies = kwargs.get('proxies')
    # cookies1 = {'JSESSIONID':'HFvnXQZM82Vw2p3dwM1S2xv25TpLpfyyRwhgpWrCp0rwZ5dQjWfq!-1667284043!NONE'}
    # cookies2 = {'JSESSIONID':'JSESSIONID=HFvnXQZM82Vw2p3dwM1S2xv25TpLpfyyRwhgpWrCp0rwZ5dQjWfq!87056699!1499084219'}
    im = get_image()
    string = get_stings(im)
    if string == 'wrong':
        return main(name=name)
    else:
        html = get_html(name,string)
        if u'验证码不正确' in html:
            return main(name=name)
        else:
            url_list = parse(html)
    return url_list


if __name__ == '__main__':
    # name = u'深圳前海融金所基金管理有限公司重庆分公司'
    # name = u'重庆惠民金融服务有限责任公司'#(【翻页】股东，变更，主要人员，经营异常)
    # name = u'重庆好士通房地产经纪有限公司'#(同上)
    # name = u'重庆桃花源山泉水有限公司'#(抽查检查)
    # name = u'重庆学府医院投资管理有限公司'#(股权出质)
    # name = u'重庆龙湖企业拓展有限公司'#(分支机构)
    # name = u'梁平县品之山农牧科技有限公司'#(动产抵押)
    name = u'南川区时尚通讯门市部'#(行政处罚)
    name = u'重庆康碧特食品有限公司'#(股权冻结）
    name = u'重庆工程职业技术学院招待所'
    name = u'重庆一点点'
    print main(name=name)

