#-*- coding:utf-8 -*-
# author: 'KEXH'
# source: 'guizhou'
from common import conf,CheckCode
import time
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import re
import requests
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
    from io import StringIO,BytesIO
pca = PCA(n_components=0.8, whiten=True)
svc = svm.SVC(kernel='rbf', C=10)
oj = os.path.join
oif = os.path.isfile
FLOAT_MAX = 1e100#1乘以10的100次方
Session=requests.Session()

def stretchPic(ImgPath):
    img = cv2.imread(ImgPath)
    rows, cols = img.shape[:2]
    pts_a = np.float32([[0,0],[0,50],[110,50]])
    pts_b = np.float32([[0,0],[0,50],[160,50]])
    M0 = cv2.getAffineTransform(pts_a, pts_b)
    img0 = cv2.warpAffine(img, M0, (cols-140, rows))
    pts1 = np.float32([[0, 46], [12, 4], [160, 46], [158, 4]])
    pts2 = np.float32([[8, 50], [0, 0], [160, 50], [155, 0]])
    M1 = cv2.getPerspectiveTransform(pts1, pts2)
    img1 = cv2.warpPerspective(img0, M1, (cols-140, rows))
    plt.imsave(ImgPath, img1)

def delBackGround(im, w, h):
    im1 = im.convert('HSV')
    for x in xrange(0, w):
        for y in xrange(0, h):
            pixel = im.getpixel((x,y))
            (H,S,V) = im1.getpixel((x,y))
            if sum(pixel) / 3 > 160 or x<12 or x>140:
                im.putpixel((x, y), (255, 255, 255))

def reCount(s):
    # 需要识别到的情况包括："6++1","6+88","9---6","99---66","8*9  ","99**6  ","66-00","89  ","68","6688","+9","--88"...
    count = None
    s = s.replace('cheng','*')
    s = s.replace('kongge','')
    p0 = r"\d([-+*]{1,3})\d"
    b0 = re.search(p0, s)
    if b0!=None:
        s = b0.group()
        if s[-1] not in ["+","-","*"]:
            if s[1:-1] in ["+","++","+++"]:
                count = int(s[0])+int(s[-1])
            elif s[1:-1] in ["*","**","***"]:
                count = int(s[0])*int(s[-1])
            elif s[1:-1] in ["-","--","---"]:
                count = int(s[0])-int(s[-1])
    p1 = r"(^\d{2,4}$|^\d{2,4}\s.$)"
    b1 = re.search(p1, s)
    if b1!=None and count == None:
        s = b1.group().split(" ")[0]
        count = int(s[0])-int(s[-1])
    p2 = r"^[-+*].*"
    b2 = re.search(p2, s)
    if b2!=None and count == None:
        s = b2.group().split(" ")[0]
        if s[-1] not in ["+","-","*"]:
            if s[0]=="+":
                count = 1+int(s[-1])
            elif s[0]=="-":
                count = 1-int(s[-1])
            elif s[0]=="*":
                count = 1*int(s[-1])
    return count

###############主流程函数###############

def getBoxs(im, w, h):
    imBoxs = []
    image_array = CheckCode.twoValue_1(im, 100)
    iList = []
    for i in xrange(w):
        col = image_array[i]
        if i >= 14 and np.sum(col) >= 2:
            iList.append(i)
    # 求出不连续段的起点和终点，由于数字会斜向左边，所以左边加3格
    # 如果运算符前后缺了数字，补为“1”，因为切片的时候被跳过了;如果只有两个数字，没有运算符，那就补个“-”减号。
    # “等于”两个字匹配为“空格”，不然到时候会被乱匹配。
    # 只获取第一个和第三个切片大小在某个范围之内的图片，其他不做解析比对，直接返回None。
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

def get_image():
    try:
        url = "http://218.57.139.24/securitycode?0.7371639391248581"
        headers_img = {
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Host': '218.57.139.24',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
        }
        ImgHtml = session.get(url = url, headers = headers_img, timeout = 5)
        # ImgHtml = requests.get(url = url, headers = headers_img, timeout = 5)
        file = BytesIO(ImgHtml.content)
        im = Image.open(file)
        return im
    except:
        get_image()

def getCount(im, prName):
    w_format = 32
    h_format = 23
    count = 0
    w, h = im.size
    delBackGround(im, w, h)# 去掉背景色
    im = CheckCode.highlight(im, w, h)# 去孤立点，提高对比度，并二值化
    w_format_0 = 160
    h_format_0 = 50
    image_array = CheckCode.twoValue_2(im, 100)
    im = CheckCode.formatImg_2(w_format_0, h_format_0, im, w, h)# 统一图片大小
    imBoxs = getBoxs(im, w, h)
    w_format = 32
    h_format = 23
    countStr = CheckCode.boxs2countStr(imBoxs, w_format, h_format, prName)
    count = reCount(countStr)
    return count

def get_main():
    csrf = ""
    url = "http://218.57.139.24/"
    headers = {
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Host': '218.57.139.24',
        'Referer': 'http://218.57.139.24/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
            }
    req = Session.get(url=url, headers=headers, timeout=10)
    # req = requests.get(url=url, headers=headers, timeout=10)
    html = req.text
    cookies = req.cookies
    if len(str(cookies).split(" "))>1:
        cookies = (str(cookies).split(" ")[1]).split("=")[1]
    else:
        cookies = ""#空cookies也可以得到页面结果的
    # print cookies
    # print html
    p = '\svalue\=.{38,98}'
    b = re.search(p, html)
    if b != None:
        s = b.group()
        csrf = s.split('"')[1]
        # print csrf
    return csrf, cookies

def get_param(company_name, count, csrf, cookies):
    # print "get param"
    param = ""
    url = "http://218.57.139.24/pub/indsearch"
    headers_info = {
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Host': '218.57.139.24',
            'Referer': 'http://218.57.139.24/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
                    }
    data = {
        "_csrf": csrf,
        "kw": company_name,
        "secode": count
    }
    cookies = {"JSESSIONID": cookies}
    req = Session.post(url=url, headers=headers_info, data=data, timeout=10)
    # req = requests.post(url=url, headers=headers_info, data=data, timeout=10, cookies=cookies)
    html = req.text
    # print html
    p = "\senckeyword\=.{34,128}"
    b = re.search(p, html)
    if b != None:
        s = b.group()
        param = s.split("'")[1]
    # print "param:",param
    return param

def get_html(param, csrf, cookies):
    url = "http://218.57.139.24/pub/search"
    headers_info = {
            # 'Accept': 'application/json, text/javascript, */*; q=0.01',
            # 'Accept-Encoding': 'gzip, deflate',
            # 'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
            # 'X-Requested-With': 'XMLHttpRequest',
            # 'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Host': '218.57.139.24',
            'Connection': 'keep-alive',
            'Referer': 'http://218.57.139.24/pub/indsearch',
            'X-CSRF-TOKEN': csrf
                }
    data = {"param": param}
    cookies = {"JSESSIONID": cookies}
    # print "cookies:",cookies
    req = Session.post(url=url, headers=headers_info, data=data, timeout=10, cookies=cookies)
    # req = requests.post(url=url, headers=headers_info, data=data, timeout=10, cookies=cookies)
    listPage = req.text
    return listPage

def main(name):
    prName = "c7_shandong"
    csrf, cookies = get_main()
    print "from home:",cookies
    if csrf == "":
        return main(name)
    else:
        im = get_image()
        if im == None:
            return main(name)
        else:
            timestr = time.strftime('%Y-%m-%d_%H-%M-%S')
            ImgDir = os.path.join(conf.ImgBaseDir, prName + "_img", )
            ImgPath_basic = ImgDir + timestr + "_" + "basic.jpg"
            im.save(ImgPath_basic)
            stretchPic(ImgPath_basic)#将图片拉伸，使斜字体变正方
            im = Image.open(ImgPath_basic)
            count = getCount(im, prName)
            if count==None:
                return main(name)
            else:
                # count，进行md5加密
                m = hashlib.md5()
                m.update(str(count))
                count = m.hexdigest()
                param = get_param(name, count, csrf, cookies)
                print param, "****csrf:",csrf
                # if param == "":
                #     return main(name)
                # else:
                listPage = get_html(param, csrf, cookies)
                jsonA = json.loads(listPage)
                if jsonA == {}:
                    return main(name)
                else:
                    return jsonA

if __name__ == "__main__":
    namelist = [
        '城阳区金宏晟制衣厂',
        '青岛春天之星大药房医药连锁有限公司',
        '青岛赛成商贸有限公司',
        '城阳区德雅轩工艺品配件商社',
        '青岛千语网络信息技术有限公司',
        '青岛三祥科技股份有限公司',
        '青岛海王纸业股份有限公司',
        '平度市静一名人饭堂',
        '黄岛海关机关服务中心',
        '青岛丹香食品有限公司',
        '青岛星河联信网络科技有限公司',

    ]
    for name in namelist:
        url_list = main(name)
        if len(url_list)>0:
            print "%s,#%s" % (str(url_list[0]), name)
        else:
            print "empty.."
        time.sleep(20)