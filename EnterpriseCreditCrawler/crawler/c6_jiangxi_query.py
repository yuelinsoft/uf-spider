#-*- coding:utf-8 -*-
# author: 'KEXH'
# source: 'shandong'
from common import conf,CheckCode
import time
import numpy as np
import sys
import os
import re
import base64
import requests
import json
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


def delBackGround(im, w, h):
    im1 = im.convert('HSV')
    for x in xrange(0, w):
        for y in xrange(0, h):
            pixel = im.getpixel((x,y))
            (H,S,V) = im1.getpixel((x,y))
            if sum(pixel) / 3 > 150:# or S<60:
                im.putpixel((x, y), (255, 255, 255))

def reCount(s):
    # 需要识别到的情况包括：...
    count = None
    s = s.replace('cheng','*')
    s = s.replace('kongge','')
    p0 = r"4{3,8}"
    b0 = re.search(p0, s)
    if b0 != None:
        s = b0.group()
        return count
    p1 = r"^\d[-+]{1,2}\d"
    b1 = re.search(p1, s)
    if b1 != None:
        s = b1.group()
        if s[1:-1]=="++"or s[1:-1]=="+":
            count = int(s[0])+int(s[-1])
        elif s[1:-1]=="--"or s[1:-1]=="-":
            count = int(s[0])-int(s[-1])
        elif s[1:-1]=="**"or s[1:-1]=="*":
            count = int(s[0])*int(s[-1])
    return count

###############主流程函数###############
def getBoxs(im, w, h):
    imBoxs = []
    image_array = CheckCode.twoValue_1(im, 100)
    iList = []
    for i in xrange(w):
        col = image_array[i]
        if i >= 1 and np.sum(col) >= 2:
            iList.append(i)
    jList = []
    for j in range(2,150):
        if j in iList:
            if (j - 1) in iList and (j + 1) not in iList:
                jList.append(j)
            elif (j - 1) not in iList and (j + 1) in iList:
                jList.append(j)
    # print jList
    if jList[0]>=10:
        jList = [2]+jList
    # print jList
    kList = []
    for k in range(0, len(jList) // 2):
        if jList[k * 2 + 1] - jList[k * 2] > 3:
            kList.append((jList[k * 2], jList[k * 2 + 1]))
    # print kList
    for m in kList:
        box = (m[0], 1, m[1], 19)
        im_box = im.crop(box)
        imBoxs.append(im_box)
    return imBoxs

def get_image():#cookies):
    try:
        url = 'http://gsxt.jxaic.gov.cn/warningetp/reqyzm.do?r=1470215421313'#'http://gsxt.jxaic.gov.cn/ECPS/common/common_getJjYzmImg.pt?yzmName=searchYzm&imgWidth=180&yzmtype=&t=0.17075443359981457'
        headers_info_2 = {
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Host': 'gsxt.jxaic.gov.cn',
            # 'Referer':'http://gsxt.gzgs.gov.cn/list.jsp',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
            'Connection': 'keep-alive'
        }
        CImages_html=session.get(url=url,headers=headers_info_2,timeout = 5)
        file  = BytesIO(CImages_html.content)
        im = Image.open(file)
        return im
    except:
        get_image()#cookies)

def getCount(im, prName):
    count = None
    w, h = im.size
    delBackGround(im, w, h)# 去掉背景色
    im = CheckCode.highlight(im, w, h)# 去孤立点，提高对比度，并二值化
    imBoxs = getBoxs(im, w, h)
    w_format = 32
    h_format = 20
    countStr = CheckCode.boxs2countStr(imBoxs, w_format, h_format, prName)
    count = reCount(countStr)
    return count

def get_html(company_name, count):
    url = "http://gsxt.jxaic.gov.cn/warningetp/yzm.do"#"http://gsxt.gzgs.gov.cn/query!searchSczt.shtml"
    headers_info = {
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Host': 'gsxt.jxaic.gov.cn',
                    # 'Referer': 'http://gsxt.jxaic.gov.cn/index.jsp?ename=6J6N6YeR5omA&liketype=qyxy',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
                }
    data = {
            # 'searchtext': company_name,
            'inputvalue': count
            }
    req = Session.post(url=url, headers=headers_info,data=data,timeout=10)
    html = req.text
    url = "http://gsxt.jxaic.gov.cn/search/queryenterpriseinfoindex.do"
    headers_info = {
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Host': 'gsxt.jxaic.gov.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
                }
    data = {
        'ename':  base64.encodestring(company_name),
        'liketype': 'qyxy',
        'pageIndex': '0',
        'pageSize': '10'
        }
    req = Session.post(url=url, headers=headers_info, data=data, timeout=10)
    return req.text

def append_list(jsonA):
    url_list = []
    info = jsonA["data"]
    if info != []:
        for i in info:#k,qylx,searchT
            tag_pripid = base64.encodestring(i["PRIPID"])[:-2]
            tag_zchregno = base64.encodestring(i["REGNO"])[:-2]
            tag_regno = base64.encodestring(i["REGNO"])[:-2]
            url_list.append([tag_pripid, tag_zchregno, tag_regno])
    return url_list

def main(name):
    prName = "c6_jiangxi"# province name,省份名称
    path_py = os.path.abspath(os.path.dirname(sys.argv[0]))
    im = get_image()
    if im == None:
        print "ldjdl"
        return main(name)
    else:
        count = getCount(im, prName)
        if count==None:
            return main(name)
        else:
            # name需要经过Base64编码
            content = get_html(name, count)
            jsonA = json.loads(content)
            if jsonA == {}:
                url_list = []
            else:
                if jsonA.has_key("data")==False:
                    return main(name)
                else:
                    url_list = append_list(jsonA)
        return url_list

if __name__ == "__main__":
    namelist = [
        # 下面这些要去看看是不是逻辑问题：
        # empty..青岛宝利丰气体有限公司
        # empty..赣州市章贡区沙河镇中心小学
        # empty..广州卓和房地产顾问有限公司
        # empty..上海卫钢建筑装饰工程有限公司
        # empty..南昌市锅炉设备安装公司赣州项目部
        # empty..上海麦萨餐饮有限公司
        # empty..赣州市公安局交警支队直属大队三中队
        # empty..广州市海珠区登涛服饰厂
        # empty..南宁市馨雨徽商贸有限公司
        # empty..芜湖金冠船务有限公司
        # empty..上海麦萨餐饮有限公司
        # empty..安徽省利特环保技术有限公司
        # empty..安徽信德商务咨询有限公司
        # empty..兴国县建筑勘察设计院
        # empty..宁都县圣龙工程装饰设计有限公司
        '上海麦萨餐饮有限公司',
        '赣州市公安局交警支队直属大队三中队',
        '章贡区蓉蓉日用品商行',
        '赣州杜兰商贸有限公司',
        '中国太平洋财产保险股份有限公司赣州中心支公司',
        '广州市海珠区登涛服饰厂',
        '南宁市馨雨徽商贸有限公司',
        '潭口兴业针织厂',
        '芜湖金冠船务有限公司',
        '江西汇康装饰工程有限公司',
        '上海麦萨餐饮有限公司',
        '赣州建大农林发展有限公司',
        '赣州盛誉装饰有限公司',
        '南康区鹏古铝合金制品加工部',
        '赣州市奇峰园林绿化工程有限公司',
        '安徽省利特环保技术有限公司',
        '兴国银创家居装饰有限公司',
        '宁都县明强电子产品有限公司',
        '安徽信德商务咨询有限公司',
        '章贡区腾飞餐馆',
        '兴国县建筑勘察设计院',
        '崇义县丰州乡毛利竹制品厂',
        '赣州非常柒加壹装饰工程有限公司',
        '大余县嘉和商贸有限责任公司',
        '赣州市南康区华亨气站',
        '宁都县圣龙工程装饰设计有限公司',

    ]
    # for i in range(1):
    #     print main(namelist[0])
    #     time.sleep(5)
    for name in namelist:
        url_list = main(name)
        if len(url_list)>0:
            print "%s,#%s" % (str(url_list[0]), name)
        else:
            print "empty..",name
        time.sleep(2)

