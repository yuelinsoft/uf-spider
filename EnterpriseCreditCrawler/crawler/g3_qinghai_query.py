#-*- coding:utf-8 -*-
# author: 'KEXH'
# source: 'anhui', 'jiangxi'
from common import conf,CheckCode
import re
import time
import requests
import numpy as np
from PIL import Image
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO,BytesIO
from sklearn.decomposition import PCA
from sklearn import svm
pca = PCA(n_components=0.8, whiten=True)
svc = svm.SVC(kernel='rbf', C=10)
Session=requests.Session()

#拿cookies
def get_cookies():
    main_url='http://218.95.241.36/search.jspx'
    headers_info_0={
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Host':'218.95.241.36',
        'Proxy-Connection':'keep-alive',
        'Referer':'http://218.95.241.36/',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    main_html=Session.get(url=main_url,headers=headers_info_0,timeout = 100)
    cookies_code=dict(main_html.cookies)
    return cookies_code

def get_image(cookies):
    url = 'http://218.95.241.36/validateCode.jspx?'#type=0&id=0.9897950897702055'
    headers_info_2 = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Host': 'Host: 218.95.241.36',
        'Referer':'http://218.95.241.36/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Proxy-Connection': 'keep-alive'
    }
    params_info_1={
        'type':'0',
        'id':'0.9897950897705055'
    }
    CImages_html=Session.get(url=url,headers=headers_info_2,params=params_info_1,cookies=cookies,timeout = 10)
    file  = BytesIO(CImages_html.content)
    im = Image.open(file)
    # im.show()
    return im

def delBackGround(im, w, h):
    im1 = im.convert('HSV')
    for x in xrange(0, w):
        for y in xrange(0, h):
            pixel = im.getpixel((x,y))
            (H,S,V) = im1.getpixel((x,y))
            if S < 40 and sum(pixel)> 100:
                im.putpixel((x, y), (255, 255, 255))
            if sum(pixel) / 3 > 150:
                im.putpixel((x, y), (255, 255, 255))

def reCount(s):
    '''需要处理的情况有：4*1, 8/2, 1++0, 5++1, 8-4, 16/8'''
    count = None
    s = s.replace('cheng','*')
    s = s.replace('kongge','')
    s = s.replace('chu','/')
    p1 = r"^\d[-+*/]{1,2}\d"
    b1 = re.search(p1, s)
    if b1 != None:
        s = b1.group()
        if s[1:-1]=="++"or s[1:-1]=="+":
            count = int(s[0])+int(s[-1])
        elif s[1:-1]=="--"or s[1:-1]=="-":
            count = int(s[0])-int(s[-1])
        elif s[1:-1]=="**"or s[1:-1]=="*":
            count = int(s[0])*int(s[-1])
        elif s[1:-1]=="//"or s[1:-1]=="/":
            count = int(s[0])/int(s[-1])
        return count
    p2 = r"^\d\d[-+*/]{1,2}\d"
    b2 = re.search(p2, s)
    if b2 != None:
        s = b2.group()
        if s[2:-1]=="++"or s[2:-1]=="+":
            count = (int(s[0])*10+int(s[1]))+int(s[-1])
        elif s[2:-1]=="--"or s[2:-1]=="-":
            count = (int(s[0])*10+int(s[1]))-int(s[-1])
        elif s[2:-1]=="**"or s[2:-1]=="*":
            count = (int(s[0])*10+int(s[1]))*int(s[-1])
        elif s[2:-1]=="//"or s[2:-1]=="/":
            count = (int(s[0])*10+int(s[1]))/int(s[-1])
        return count
    return None

def getBoxs(im, w, h):
    imBoxs = []
    image_array = CheckCode.twoValue_1(im, 100)
    iList = []
    for i in xrange(w):
        col = image_array[i]
        if i >= 1 and np.sum(col) >= 2:
            iList.append(i)
    jList = []
    for j in range(1,150):
        if j in iList:
            if (j - 1) in iList and (j + 1) not in iList:
                jList.append(j)
            elif (j - 1) not in iList and (j + 1) in iList:
                jList.append(j)
    kList = []
    for k in range(0, len(jList) // 2):
        if jList[k * 2 + 1] - jList[k * 2] > 3:
            kList.append((jList[k * 2], jList[k * 2 + 1]))
    # print kList
    for m in kList:
        yList = []
        for y in xrange(h):
            line = image_array[:,y:y+1][m[0]:m[1]]
            if np.sum(line) >= 2:
                yList.append(y)
        if yList != []:
            box = (m[0]-1, yList[0]-1, m[1]+1, yList[-1]+1)
        else:
            box = (m[0]-1, 10, m[1]+1, 40)
        im_box = im.crop(box)
        imBoxs.append(im_box)
    return imBoxs

    # a = im.getcolors(maxcolors=15000)
    # box_0 = (106,0,120,20)
    # im_0 = im.crop(box_0)
    # b = im_0.getcolors(maxcolors=15000)
    # if a[0][0]>=10150:
    #     if b[0][0]>=450:#纯算式，且要切成5格的
    #         cutList = [1,28,47,64,85,109]
    #         resize = 1.15
    #         area_1 = (82,0,97,20)
    #         whitepoints = 520
    #         displace = 0
    #         imBoxs = crop(im, w, h, cutList, resize, area_1, whitepoints, displace)
    #     else:#纯算式，且要切成6格的
    #         cutList = [1,29,51,68,85,102,120]
    #         resize = 1
    #         imBoxs = crop(im, w, h, cutList, resize)
    # else:#带汉字的，且要切成六格的
    #     cutList = [1,29,64,83,120,152,180]
    #     resize = 1.176
    #     area_1 = (160, 0, 180, 20)
    #     whitepoints = 725
    #     displace = 6
    #     imBoxs = crop(im, w, h, cutList, resize, area_1, whitepoints, displace)
    # return imBoxs

def getCount(im, prName):
    count = None
    w, h = im.size
    delBackGround(im, w, h)# 去掉背景色
    im = CheckCode.highlight(im, w, h)# 去孤立点，提高对比度，并二值化
    imBoxs = getBoxs(im, w, h)
    w_format = 30
    h_format = 30
    countStr = CheckCode.boxs2countStr(imBoxs, w_format, h_format, prName)
    count = reCount(countStr)
    return count

def get_html(name,checkNo,cookies):
    link_list = []
    check_url='http://218.95.241.36/checkCheckNo.jspx'
    headers_info_3 = {
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Host': '218.95.241.36',
        'Origin':'http://218.95.241.36',
        'Referer':'http://218.95.241.36/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
        'X-Requested-With':'XMLHttpRequest'
    }
    data_info={
        'checkNo':checkNo
    }
    r = Session.post(url=check_url,headers=headers_info_3,data=data_info,cookies=cookies,timeout = 10)
    # print r.text
    # 以上部分已经调通。
    search_list='http://218.95.241.36/searchList.jspx'
    headers_info_4 = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Connection':'keep-alive',
        'Host': '218.95.241.36',
        'Origin':'http://218.95.241.36',
        'Referer':'http://218.95.241.36/search.jspx',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    data_info_2={
        'checkNo' : checkNo,
        'entName' : name
    }
    search_html=Session.post(url=search_list,headers=headers_info_4,data=data_info_2,timeout = 10)
    content = search_html.content
    return content

def main(name):
    prName = "g3_qinghai"# province name,省份名称
    cookies = get_cookies()
    im = get_image(cookies)
    count = getCount(im, prName)
    if count == None:
        return main(name)
    # 以上这些步骤都能走通了。get_html里面有部分未调通，已备注。
    listPage = get_html(name,str(count),cookies)
    result_list = common.parse_url(listPage, 'li', 'font16', 'li', 'width:95%')
    if result_list == None:
        return main(name)
    else:
        return result_list

if __name__ == "__main__":
    namelist = [
        # '青海省海北铝业有限公司',
        # '青海省西海煤电有限责任公司',
        # '青海省西海煤炭开发有限责任公司',
        # '青海省奥凯煤业发展集团有限责任公司',
        # '青海互助青稞酒有限公司',
        # '化隆县先奇铝业有限公司',
        # '青海民镁科技股份有限公司',
        # '青海民和金属冶炼总公司',
        # '青海乐都华夏水泥有限公司',
        # '青海西威水泥股份有限公司',
        # '民和昌盛冶金有限公司',
        # '青海青乐化工机械有限责任公司',
        # '青海省民和湟川冶金有限公司',
        # '青海东风模锻有限责任公司',
        # '青海乐天玻璃制品有限公司',
        # '青海通力铁合金有限公司',
        # '青海民和青锋工贸有限责任公司',
        # '青海省三江水电开发',
        # '兴海县赛什墉铜矿有限公司',
        # '海南州金谊油脂工业有限责任公司',
        # '中国石油天然气股份有限公司青海油田分公司',
        # '西部矿业股份有限公司锡铁山分公司',
        # '青海盐湖工业集团有限公司',
        # '格尔木藏格钾肥有限公司',
        # '青海省盐业股份有限公司',
        # '青海庆华矿业有限责任公司',
        # '青海翰海集团有限公司',
        # '青海西旺矿业开发有限公司',
        # '茫崖康泰钾肥开发有限公司',
        # '碱业'
        # '青海兆天商贸有限公司',
        '青海森旭养殖有限公司'
    ]
    for name in namelist:
        url_list = main(name)
        if len(url_list) > 0:
            print "'%s', # %s" % (str(url_list[0]), name)
        else:
            print "empty..", name
        time.sleep(2)

