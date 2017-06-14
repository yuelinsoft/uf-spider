#-*- coding:utf-8 -*-
# author: 'KEXH'
from common import conf,common,CheckCode
from PIL import ImageDraw
import requests
import operator
from PIL import Image
import pytesseract
from difflib import SequenceMatcher
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO
Session=requests.Session()
with open (conf.dictoryPath,'r') as f3:
    #成语库
    dictory =f3.readlines()

def get_image(cookies):
    try:
        url = 'http://xyjg.egs.gov.cn/ECPS_HB/validateCode.jspx?type=1&_='
        headers_info_2 = {
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Host': 'xyjg.egs.gov.cn',
            'Referer':'http://xyjg.egs.gov.cn/ECPS_HB/search.jspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
            'Proxy-Connection': 'keep-alive'
        }
        params_info_1={
            'type':'1',
            '_':''
        }
        CImages_html=Session.get(url=url,headers=headers_info_2,params=params_info_1,cookies=cookies,timeout = 5)
        file  = BytesIO(CImages_html.content)
        im = Image.open(file)
        return im
    except:
        get_image(cookies)


def image_clean(im):
    w,h = im.size
    for y in range(h):
        for x in range(w):
            pixel = im.getpixel((x, y))
            if sum(pixel)/3 >200:
                im.putpixel((x, y),(255,255,255))
            else:
                im.putpixel((x,y),(0, 0, 0))
    return im


def twoValue(image,G):
    t2val = {}
    for y in xrange(0,image.size[1]):
        for x in xrange(0,image.size[0]):
            g = image.getpixel((x,y))
            if g > G:
                t2val[(x,y)] = 1
            else:
                t2val[(x,y)] = 0
    return t2val


def clearNoise(t2val,image,N,Z):
    size = image.size
    for i in xrange(0,Z):
        t2val[(0,0)] = 1
        t2val[(image.size[0] - 1,image.size[1] - 1)] = 1
        for x in xrange(1,image.size[0] - 1):
            for y in xrange(1,image.size[1] - 1):
                nearDots = 0
                L = t2val[(x,y)]
                if L == t2val[(x - 1,y - 1)]:
                    nearDots += 1
                if L == t2val[(x - 1,y)]:
                    nearDots += 1
                if L == t2val[(x- 1,y + 1)]:
                    nearDots += 1
                if L == t2val[(x,y - 1)]:
                    nearDots += 1
                if L == t2val[(x,y + 1)]:
                    nearDots += 1
                if L == t2val[(x + 1,y - 1)]:
                    nearDots += 1
                if L == t2val[(x + 1,y)]:
                    nearDots += 1
                if L == t2val[(x + 1,y + 1)]:
                    nearDots += 1
                if nearDots < N:
                    t2val[(x,y)] = 1
    image = Image.new("1",size)
    draw = ImageDraw.Draw(image)
    for x in xrange(0,size[0]):
        for y in xrange(0,size[1]):
            draw.point((x,y),t2val[(x,y)])
            # 清理边界， 如果大于或者小于某个值 就清空
            if x < 9 or y < 4 or x > 140 or y > 37:
                image.putpixel((x, y), 1)
    return image


def get_sting (im):
    string = pytesseract.image_to_string(im, lang='chi_sim',config ='-psm 7').strip()
    string = CheckCode.replaceStr(string)
    rank_dic = {}
    for a in dictory:
        a = a.replace('\n','')
        ratio = SequenceMatcher(None,a,string).ratio()
        if ratio > 0:
            rank_dic.update({a : ratio})
    if len(rank_dic) < 1:
        return 'wrong'
    else:
        string = max(rank_dic.items(),key=operator.itemgetter(1))[0]
        return string


def get_html(name,string,cookies):
    check_url='http://xyjg.egs.gov.cn/ECPS_HB/checkCheckNo.jspx'
    headers_info_3 = {
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Host': 'xyjg.egs.gov.cn',
            'Referer':'http://xyjg.egs.gov.cn/ECPS_HB/search.jspx',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
        }
    data_info={
        'checkNo':string
    }
    req = Session.post(url=check_url,headers=headers_info_3,data=data_info,cookies=cookies,timeout = 10)
    if 'true' in req.content:
        search_list='http://xyjg.egs.gov.cn/ECPS_HB/searchList.jspx'
        headers_info_4 = {
                'Accept-Encoding':'gzip, deflate',
                'Accept-Language':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Host': 'xyjg.egs.gov.cn',
                'Connection' : 'keep-alive',
                'Referer':'http://xyjg.egs.gov.cn/ECPS_HB/search.jspx',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
            }
        data_info_2={
            'checkNo' : string,
            'entName' : name
        }
        search_html=Session.post(url=search_list,headers=headers_info_4,data=data_info_2,cookies=cookies,timeout = 10)
        content = search_html.content
        return content


def main(name):
    cookies = {'JSESSIONID':'0000dTRJoou3-cXGhEt8xZTJNma:-1', 'hbgjs':'52705030'}
    im = get_image(cookies)
    if im == None:
        return main(name)
    else:
        im = image_clean(im)
        image =im.convert("L")
        t2val = twoValue(image,220)
        im = clearNoise(t2val,image,2,8)
        string = get_sting(im)
        listPage = get_html(name,string,cookies)
        result_list = common.parse_url(listPage, 'li', 'font16')
        if result_list == None:
            return main(name)
        else:
            return result_list


name = '融金所'
print main(name)