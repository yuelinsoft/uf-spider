# -*- coding:utf-8 -*-
# author: 'KEXH'
# source: 'shandong'
from common import conf,common,CheckCode
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import requests
from bs4 import BeautifulSoup
import json
import hashlib
from PIL import Image
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
    from io import StringIO, BytesIO
pca = PCA(n_components=0.8, whiten=True)
svc = svm.SVC(kernel='rbf', C=10)
oj = os.path.join
oif = os.path.isfile
FLOAT_MAX = 1e100  # 1乘以10的100次方
Session = requests.Session()


'''
调通关键接口需要走的流程包括：
1. get 到 robotcookieid, csrf
2. get_image()
3. get_count
4. to_indsearch传name, secode等，并get到param
5. to_search传param
'''

def reCount(s):
    count = None
    replace_dict = {'cheng': '*', 'kongge': '', '++': '+', '--': '-', '**': '*'}
    for re_d in replace_dict:
        s = s.replace(re_d, replace_dict[re_d])
    _p = r"^[-+*]"
    _b = re.search(_p, s)
    if _b != None:
        s = "1" + s
    p_ = r"[-+*]$"
    b_ = re.search(p_, s)
    if b_ != None:
        s = s + "1"
    p0 = r"\d[-+*]\d"
    b0 = re.search(p0, s)
    if b0 != None:
        s = b0.group()
        if s[1] == "+":
            count = int(s[0]) + int(s[2])
        elif s[1] == "*":
            count = int(s[0]) * int(s[2])
        elif s[1] == "-":
            count = int(s[0]) - int(s[2])
    p1 = r"(^\d{2})"
    b1 = re.search(p1, s)
    if b1 != None and count == None:
        count = int(s[0]) - int(s[-1])
    return count

def stretchPic(ImgPath):
    img = cv2.imread(ImgPath)
    rows, cols = img.shape[:2]
    pts_a = np.float32([[0, 0], [0, 50], [110, 50]])
    pts_b = np.float32([[0, 0], [0, 50], [160, 50]])
    M0 = cv2.getAffineTransform(pts_a, pts_b)
    img0 = cv2.warpAffine(img, M0, (cols - 140, rows))
    pts1 = np.float32([[0, 46], [12, 4], [160, 46], [158, 4]])
    pts2 = np.float32([[8, 50], [0, 0], [160, 50], [155, 0]])
    M1 = cv2.getPerspectiveTransform(pts1, pts2)
    img1 = cv2.warpPerspective(img0, M1, (cols - 140, rows))
    plt.imsave(ImgPath, img1)

def delBackGround(im, w, h):
    im1 = im.convert('HSV')
    for x in xrange(0, w):
        for y in xrange(0, h):
            pixel = im.getpixel((x, y))
            (H, S, V) = im1.getpixel((x, y))
            # if S < 40 and sum(pixel)> 100:
            #     im.putpixel((x, y), (255, 255, 255))
            if sum(pixel) / 3 > 155 or x < 12 or x > 132:
                im.putpixel((x, y), (255, 255, 255))

def getBoxs(im, w, h):
    imBoxs = []
    image_array = CheckCode.twoValue_1(im, 100)
    iList = []
    for i in xrange(w):
        col = image_array[i]
        if i >= 14 and np.sum(col) >= 2:
            iList.append(i)
    jList = []
    for j in range(14, 140):
        if j in iList:
            if (j - 1) in iList and (j + 1) not in iList:
                jList.append(j)
            elif (j - 1) not in iList and (j + 1) in iList:
                jList.append(j)
    kList = []
    for k in range(0, len(jList) // 2):
        if jList[k * 2 + 1] - jList[k * 2] > 3:
            kList.append((jList[k * 2] - 3, jList[k * 2 + 1] + 2))
    # print kList
    for m in kList:
        box = (m[0], 12, m[1], 35)
        im_box = im.crop(box)
        imBoxs.append(im_box)
    return imBoxs

def getCount(im, prName):
    count = None
    w, h = im.size
    delBackGround(im, w, h)  # 去掉背景色
    im = CheckCode.highlight(im, w, h)  # 去孤立点，提高对比度，并二值化
    w_format_0 = 160
    h_format_0 = 50
    image_array = CheckCode.twoValue_2(im, 100)
    im = CheckCode.formatImg_2(w_format_0, h_format_0, im, w, h)  # 统一图片大小
    imBoxs = getBoxs(im, w, h)
    w_format = 30
    h_format = 30
    countStr = CheckCode.boxs2countStr(imBoxs, w_format, h_format, prName)
    count = reCount(countStr)
    return count

def get_home(robotcookieid, csrf):
    url = "http://211.141.74.198:8081/aiccips/"
    headers_img = {
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Host': '211.141.74.198:8081',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    if robotcookieid==None:
        req = Session.get(url, headers=headers_img, timeout=140)
    else:
        cookies = {
            'ROBOTCOOKIEID': robotcookieid
        }
        req = Session.get(url, headers=headers_img, cookies=cookies, timeout=140)
    content = req.text
    try:
        if len(content)<1000:
            p = r"\w{40}"
            b = re.search(p,str(content))
            robotcookieid =  b.group()
        else:
            pageSoup = BeautifulSoup(content, 'lxml')
            a = pageSoup.findAll('meta')[3]
            b = re.search('''content=.*''',str(a))
            if b != None:
                csrf = b.group().split('"')[1]
    except:
        get_home(robotcookieid, csrf)
    return robotcookieid, csrf

def get_image(robotcookieid):
    url = "http://211.141.74.198:8081/aiccips/securitycode?0.7315294243537567"
    headers_img = {
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Host': '211.141.74.198:8081',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    cookies = {
        'ROBOTCOOKIEID': robotcookieid
    }
    try:
        ImgHtml = Session.get(url = url, headers = headers_img, cookies=cookies, timeout = 140)
        file = BytesIO(ImgHtml.content)
        im = Image.open(file)
        return im
    except:
        get_image(robotcookieid)

def to_indsearch(robotcookieid, csrf, name, secode):
    param = ""
    url = "http://211.141.74.198:8081/aiccips/pub/indsearch"
    headers = {
        'Host': '211.141.74.198:8081',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Origin': 'http://211.141.74.198:8081',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Referer': 'http://211.141.74.198:8081/aiccips/',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8'
    }
    cookies = {
        'ROBOTCOOKIEID': robotcookieid
    }
    data = {
        'kw': name,
        '_csrf': csrf,
        'secode': secode
    }
    req = Session.post(url=url,headers=headers,data=data,cookies=cookies,timeout=140)
    content = req.text
    print  content
    pageSoup = BeautifulSoup(content, 'lxml')
    a = pageSoup.findAll('script')[4]
    b = re.search("enckeyword='(.*?)'",str(a))
    if b != None:
        param = b.group()
    return param

def to_search(param, csrf, robotcookieid):
    url = "http://211.141.74.198:8081/aiccips/pub/search"
    headers = {
        'Host': '211.141.74.198:8081',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Origin': 'http://211.141.74.198:8081',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Referer': 'http://211.141.74.198:8081/aiccips/pub/indsearch',
        'X-CSRF-TOKEN': csrf
    }
    cookies = {
        'ROBOTCOOKIEID': robotcookieid
    }
    data = {
        'param': param
    }
    req = Session.post(url=url,headers=headers,data=data,cookies=cookies,timeout=140)
    content = req.text
    if len(content)<5:
        return None
    else:
        jsonA = json.loads(content)
        return jsonA

def main(name):
    prName = "b2_jilin"# province name,省份名称
    robotcookieid = None
    csrf = ""
    while robotcookieid==None or csrf=="":
        robotcookieid, csrf = get_home(robotcookieid, csrf)
    print robotcookieid, csrf
    im = get_image(robotcookieid)
    if im == None:
        return main(name)
    else:
        im.show()
        timestr = time.strftime('%Y-%m-%d_%H-%M-%S')
        ImgDir = os.path.join(conf.ImgBaseDir, prName + "_img", )
        ImgPath_basic = ImgDir + timestr + "_" + "basic.jpg"
        im.save(ImgPath_basic)
        stretchPic(ImgPath_basic)  # 将图片拉伸，使斜字体变正方
        im = Image.open(ImgPath_basic)
        count = getCount(im, prName)
        if count == None:
            return main(name)
        else:
            m = hashlib.md5()
            m.update(str(count))
            secode = m.hexdigest()
            param = to_indsearch(robotcookieid, csrf, name, secode)
            result = to_search(param, csrf, robotcookieid)

if __name__ == "__main__":
    namelist = [
        '腾讯'
    ]
    for name in namelist:
        main(name)
        # url_list = main(name)
        # if len(url_list) > 0:
        #     print "'%s', # %s" % (str(url_list[0]), name)
        # else:
        #     print "empty..", name
        # time.sleep(2)


