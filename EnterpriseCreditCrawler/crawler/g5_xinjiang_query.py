#-*- coding:utf-8 -*-
# author: 'KEXH'
# source: 'shandong'
from common import conf,CheckCode
import time
import os
import re
import requests
from PIL import Image
from bs4 import BeautifulSoup
from sklearn.decomposition import PCA
from sklearn import svm
try:
    import psyco
    psyco.full()
except ImportError:
    pass
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO

pca = PCA(n_components=0.8, whiten=True)
svc = svm.SVC(kernel='rbf', C=10)
oj = os.path.join
oif = os.path.isfile
FLOAT_MAX = 1e100#1乘以10的100次方
Session=requests.Session()

def delBackGround(im, w, h):
    im1 = im.convert('HSV')
    for x in xrange(0, w):
        for y in xrange(0, h):
            pixel = im.getpixel((x,y))
            (H,S,V) = im1.getpixel((x,y))
            if sum(pixel) / 3 > 160 or x<2 or x>140:
                im.putpixel((x, y), (255, 255, 255))

def reCount(s):
    count = None
    s = s.replace('cheng','*')
    p0 = r"\d([+*]{1})\d"
    b0 = re.search(p0, s)
    if b0!=None:
        s = b0.group()
        if s[1] == "+":
            count = int(s[0])+int(s[2])
        elif s[1] == "*":
            count = int(s[0])*int(s[2])
    return count

###############主流程函数###############
def get_home():
    url = "http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=index&random=1471573844918"#+str(int(time.time()))
    headers_info = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
            'Host': 'gsxt.xjaic.gov.cn:7001',
            'Connection': 'keep-alive'
                }
    req = Session.get(url=url, headers=headers_info, timeout=10)
    # print req.text

def get_image():
    try:
        url = "http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=createYzm&dt=1471334103122&random=1471573845540"#+str(int(time.time()))
        headers_img = {
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Host': 'gsxt.xjaic.gov.cn:7001',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        ImgHtml = Session.get(url = url, headers = headers_img, timeout = 5)
        # ImgHtml = requests.get(url = url, headers = headers_img, timeout = 5)
        file = BytesIO(ImgHtml.content)
        im = Image.open(file)
    # im.show()
        return im
    except:
        get_image()

def getCount(im, prName):
    w_format = 32
    h_format = 23
    squares = [2,14,33,46]
    w, h = im.size
    delBackGround(im, w, h)# 去掉背景色
    im = CheckCode.highlight(im, w, h)# 去孤立点，提高对比度，并二值化
    imBoxs = []
    for i in range(3):
        box = (squares[i], 1, squares[i+1], 25)
        im_box = im.crop(box)
        imBoxs.append(im_box)
    w_format = 22
    h_format = 26
    countStr = CheckCode.boxs2countStr(imBoxs, w_format, h_format, prName)
    count = reCount(countStr)
    return count

def get_html(company_name, count):
    # url = "http://gsxt.xjaic.gov.cn:7001/keyword.do?method=keywordFilter&random="+str(int(time.time()))
    # headers_info = {
    #         'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
    #         'Host': 'gsxt.xjaic.gov.cn:7001',
    #         'Connection': 'keep-alive'
    #             }
    # data = {
    #     "method": 'keywordFilter',
    #     "qymc": '%E8%85%BE%E8%AE%AF'
    #         }
    # req = Session.post(url=url, headers=headers_info, data=data, timeout=10)

    url = "http://gsxt.xjaic.gov.cn:7001/ztxy.do?method=list&djjg=&random=1471573852282"#+str(int(time.time()))
    headers_info = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
            'Host': 'gsxt.xjaic.gov.cn:7001',
            'Connection': 'keep-alive'
                }
    data = {
        "yzm": count,
        "maent.entname": company_name.decode('utf-8').encode('gbk')
            }
    req = Session.post(url=url, headers=headers_info, data=data, timeout=10)
    html = req.text
    if len(html)<=150:
        return None
    else:
        return html

def parse_html(html):
    tagList = []
    pageSoup = BeautifulSoup(html, 'lxml')
    print pageSoup
    info = pageSoup.find('div',class_='center-1')
    linkList = info.findAll('a')
    print linkList
    p = "openView.*"
    for i in linkList:
        # print type(i),str(i)
        b = re.search(p, str(i))
        if b != None:
            s = b.group()
            tagList.append([s.split(")")[1][2:-4],(s.split(")")[0]).split("(")[1]])
    return tagList

def main(name):
    prName = "g5_xinjiang"
    get_home()
    im = get_image()
    if im == None:
        return main(name)
    else:
        count = getCount(im, prName)
        if count==None:
            return main(name)
        else:
            html = get_html(name, count)
            if html == None:
                return main(name)
            else:
                # print html
                # time.sleep(20)
                tagList = parse_html(html)
    return tagList

if __name__ == "__main__":
    namelist = [
        '青岛广元生国际货运代理有限公司',
        '上海义通通讯设备经营部',
        '上海浩淼服饰有限公司',
        '上海义通通讯设备经营部',
        '上海浩淼服饰有限公司',
        '上海柏之木贸易发展有限公司',
        '上海柏之木贸易发展有限公司',
        '上海国誉赫玛国际货运代理有限公司',
        '青岛君烨物资有限公司',
        '上海腾影文具有限公司',
        '浙江开元酒店管理有限公司上海分公司',
        '青岛君烨物资有限公司',
        '青岛成宇新能源有限公司'
    ]
    for name in namelist:
        url_list = main(name)
        if len(url_list)>0:
            print "%s,#%s" % (str(url_list[0]), name)
        else:
            print "empty.."
        time.sleep(2)

