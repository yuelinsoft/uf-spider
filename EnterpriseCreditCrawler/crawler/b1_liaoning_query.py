#-*- coding:utf-8 -*-
# author: 'KEXH'
from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
import re
import requests
import time
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO
from PIL import Image
import pytesseract
import json
from bs4 import BeautifulSoup
Session=requests.Session()

def image_to_string(im):
    w,h = im.size
    for y in range(h):
        for x in range(w):
            pixel = im.getpixel((x, y))
            if sum(pixel)/3 >175:
                im.putpixel((x, y), (255,255,255))
            else:
                im.putpixel((x,y),(0, 0, 0))
    string = pytesseract.image_to_string(im,lang='eng',config ='-psm 7').replace(' ','').replace('I/I','W')
    return string

def get_image():#cookies):
    url = 'http://gsxt.lngs.gov.cn/saicpub/commonsSC/loginDC/securityCode.action?tdate=94785'
    headers_info_2 = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Host': 'gsxt.lngs.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'Proxy-Connection': 'keep-alive',
        'Upgrade-Insecure-Requests':'1'
    }
    CImages_html=Session.get(url=url,headers=headers_info_2,timeout = 10)
    file  = BytesIO(CImages_html.content)
    im = Image.open(file)
    return im

def get_html(name,string):
    jsonA = {}
    search_list='http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/lngsSearchListFpc.action'
    headers_info_4 = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection':'keep-alive',
        'Host': 'gsxt.lngs.gov.cn',
        'Referer':'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/lngsSearchFpc.action',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }
    data_info_2={
        'authCode' : string,
        'solrCondition' : name
    }
    search_html=Session.post(url=search_list,headers=headers_info_4,data=data_info_2,timeout = 10)
    content = search_html.content
    soup = BeautifulSoup(content,'lxml')
    if soup.find ('li', style="width:95%") is None:
        link_list = []
        s = str(soup.select('script'))
        p = r"searchList_paging[\s\S]*var\scodevalidator"
        b = re.search(p,s)
        if b != None:
            lists = b.group()
            if len(lists)>40:
                lists = lists.split("]",-1)[0]+"]"
                if len(lists.split("["))>1:
                    lists = "["+lists.split("[")[1]
                    jsonA = json.loads(lists)
    else:
        jsonA = None
    return jsonA

def append_list(jsonA):
    url_list = []
    for i in jsonA:
        if i != None and i.has_key("pripid"):
            pripid = i["pripid"]
            entname = i["entname"]
            regno = i["regno"]
            enttype = i["enttype"]
            optstate = i["optstate"]
            url_list.append([pripid, entname, regno, enttype, optstate])
    return url_list

def main(name):
    im = get_image()
    string = image_to_string(im)
    jsonA = get_html(name,string)
    if jsonA == None:
        return main(name)
    elif jsonA == {}:
        url_list = []
    else:
        url_list = append_list(jsonA)
    return url_list

if __name__ == "__main__":
    namelist = [
'大连爱比利文化传播有限公司',
'大连市中山区东方日出饭店',
'中国移动通信集团辽宁有限公司大连分公司',
'大连科富液压装备制造中心',
'沙河口区鼎邦建材商行',
'瓦房店利伟轴承制造有限公司',
'庄河碧玉广告设计工作室',
'大连经济技术开发区辽河西路金帛霖美发店',
'青岛澳莘蒂彩商贸有限公司',
'大连市甘井子区静竹街乐宠时光宠物用品店',
'金州区友谊街道时美服装厂',
'大连立诚塑料机械厂',
'瓦房店市印象丽江菜馆',
'大连新商报社',
'大连市中山区竹园副食品店',
'大连市中山区斑鱼府餐饮有限公司',
'大连市中山区久里服装店',
'大连红星美业发展有限公司',
'沈阳铁路局大连客运段',
'沙河口区春柳街道香沙社区',
'大连龙福创意设计有限公司',
'驱逐舰（大连）信息技术有限公司',
'大连广兴源机械设备有限公司',
'大连丽豪硕服装辅料有限公司',
'大连诚一运输有限公司',
'大连风神物流有限公司',
'旅顺口区碧玉轩玉器商行',
'大连市双兴综合批发市场伊人丽影服饰商行',

    ]
    for name in namelist:
        url_list = main(name)
        if len(url_list)>0:
            print "%s,#%s" % (str(url_list[0]), name)
            time.sleep(2)
