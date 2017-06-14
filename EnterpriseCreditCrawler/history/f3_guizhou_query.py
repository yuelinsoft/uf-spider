#-*- coding:utf-8 -*-
# author: 'KEXH'
from __future__ import unicode_literals
from EnterpriseCreditCrawler.common import conf,captcha
import os
import re
import requests
import json
from PIL import Image
from random import random, choice
from copy import copy
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
Session=requests.Session()

pca = PCA(n_components=0.8, whiten=True)
svc = svm.SVC(kernel='rbf', C=10)
oj = os.path.join
oif = os.path.isfile
FLOAT_MAX = 1e100#1乘以10的100次方
F_guizhou_query = 5

###########聚类算法与机器学习#################
def nearest_cluster_center(point, cluster_centers):
    min_index = point[1]
    min_dist = FLOAT_MAX
    for i,cc in enumerate(cluster_centers):
        d = abs(cc[0]-point[0])
        if min_dist > d:
            min_dist = d # 某点到各个中心的距离之最小值
            min_index = i # cluster_centers的索引号，指某个中心
    return (min_index, min_dist)

def kpp(points, cluster_centers):
    # 随机选取第一个中心点
    cluster_centers[0] = copy(choice(points))

    # 列表长度为len(points)，保存每个点离最近的中心点的距离
    d = [0.0 for _ in xrange(len(points))]

    for i in xrange(1, len(cluster_centers)):
        sum = 0
        for j, p in enumerate(points):
            #第j个数据点p与各个中心点距离的最小值
            d[j] = nearest_cluster_center(p, cluster_centers[:i])[1]
            sum += d[j]
        sum *= random()

        for j, di in enumerate(d):
            sum -= di
            if sum > 0:
                continue
            cluster_centers[i] = copy(points[j])
            break

    for p in points:
        p[1] = nearest_cluster_center(p, cluster_centers)[0]

def oneDimensionKmeansPP(pointsList, nclusters):
    '''
    nearest_cluster_center和kpp被这个函数调用。
    '''
    # 对pointsPList中的点进行初始化操作
    points = []
    for p in pointsList:
        point=[p, 0]
        points.append(point)
    #根据指定的中心点个数，初始化中心点，x值均为(0.0)
    cluster_centers = []
    for cc in xrange(nclusters):
        cc=[0.0,0]
        cluster_centers.append(cc)
    # call k++ init
    kpp(points, cluster_centers) #选择初始种子点

    # kmeans
    #右移两位，即len(points)除以2的10次方（1024），约为0.1% of points
    lenpts10 = len(points) >> 10
    changed = 0
    while True:
        # group element for centroids are used as counters
        for cc in cluster_centers:
            cc[0] = 0.0
            cc[1] = 0
        for p in points:
            #与该种子点在同一簇的数据点的个数
            cluster_centers[p[1]][1] += 1
            cluster_centers[p[1]][0] += p[0]
        #生成新的中心点
        for cc in cluster_centers:
            cc[0] /= cc[1]# 有时候会出现bug:ZeroDivisionError: float division by zero

        # find closest centroid of each PointPtr
        changed = 0 # 记录所属簇发生变化的数据点的个数
        for  p in points:
            min_i = nearest_cluster_center(p, cluster_centers)[0]
            if min_i != p[1]:
                changed += 1
                p[1] = min_i

        # stop when 99.9% of points are good
        if changed <= lenpts10:
            break

    for i, cc in enumerate(cluster_centers):
        cc[1] = i
    old_cluster_centers = cluster_centers
    cluster_centers = {}
    for j in old_cluster_centers:
        cluster_centers[j[1]] = j[0]
    # pointsCount，此时的points已经具备所属簇类的属性，因此，可以统计每个簇类的点个数
    pointsCount = {}
    for i in points:
        k = i[1]
        if pointsCount.has_key(k)==False:
            pointsCount[k]=0
        pointsCount[k]=pointsCount[k]+1
    return cluster_centers, pointsCount, points

###########图片切分与比对################
def getBoxs(im, w, h):
    # 清理边缘区域和颜色淡的像素点，方便进行分格分析
    for x in xrange(0, w):
        for y in xrange(0, h):
            pixel = im.getpixel((x, y))
            if sum(pixel) / 3 > 220 or x < 33 or y < 11 or x > 221 or y > 37:
                im.putpixel((x, y), (255, 255, 255))
    centralArea1 = (125,12, 130, 35)
    im1 = im.crop(centralArea1)
    centralArea2 = (114,12, 141, 35)
    im2 = im.crop(centralArea2)
    a = im.getcolors(maxcolors=15000)
    b = im1.getcolors(maxcolors=15000)
    c = im2.getcolors(maxcolors=15000)
    sKey = 6 # 6的情况比较常见
    if a[0][0] >= 9100 and len(a) <= 1200 and b[0][0]<=108:
        sKey = 5
    elif len(a) >= 1600 or len(b) >= 20 or b[0][0] <= 80 or c[0][0] <= 400:
        sKey = 7
    return sKey

def getMainColor(im, w, h):
    '''
    nclusters, 设置每个文字格的聚类中心个数。
    cluster_centers_X, 中心点0的H值，将作为该文字格的主色。
    pointsCount_X, 中心点对应的成员个数。
    '''
    nclusters = 7
    im1 = im.convert('HSV')
    im2 = im.convert('CMYK')
    pointsList_H = []
    pointsList_C = []
    for x in xrange(0, w):
        for y in xrange(0, h):
            (H,S,V) = im1.getpixel((x,y))
            (C,M,Y,K) = im2.getpixel((x,y))
            if H != 0 and C != 0:
                pointsList_H.append(H)
                pointsList_C.append(C)
    try:
        cluster_centers_H, pointsCount_H, points_H = oneDimensionKmeansPP(pointsList_H, nclusters)
        H0 = int(cluster_centers_H[0])
        cluster_centers_C, pointsCount_C, points_C = oneDimensionKmeansPP(pointsList_C, nclusters)
        C0 = int(cluster_centers_C[0])
    except:
        H0=0
        C0=0
    finally:
        return H0, C0

def delLines(im, w, h, H0, C0):
    im1 = im.convert('HSV')
    im2 = im.convert('CMYK')
    for x in xrange(1, w-1):
        for y in xrange(1, h-1):
            (R2,G2,B2) = im.getpixel((x,y-1))
            (R3,G3,B3) = im.getpixel((x,y+1))
            (H,S,V) = im1.getpixel((x,y))
            (H2,S2,V2) = im1.getpixel((x,y-1))
            (H3,S3,V3) = im1.getpixel((x,y+1))
            (C,M,Y,K) = im2.getpixel((x,y))
            (C2,M2,Y2,K2) = im2.getpixel((x,y-1))
            (C3,M3,Y3,K3) = im2.getpixel((x,y+1))
            # 执行过滤标准一
            if abs(H - H0) > 35 and abs(H2 - H0) <= 35 and abs(H3 - H0) <= 35:
                im.putpixel((x,y), ((R2+R3)//2,(G2+G3)//2,(B2+B3)//2))
            elif abs(C - C0) > 35 and abs(C2 - C0) <= 35 and abs(C3 - C0) <= 35:
                im.putpixel((x,y), ((R2+R3)//2,(G2+G3)//2,(B2+B3)//2))
            elif abs(H - H0) > 35 and abs(C - C0) > 35:
                im.putpixel((x,y), (255,255,255))

def rmSinglePoints(im, w, h):
    '''
    [去孤立点]当小于N时，无论中心点是什么颜色，都会被置为白色；如果中心点原先为白色，大于N的话，一样跳过.
    :param G: 判定临近点是否算有颜色的基准值
    :param N: 有颜色的临近点个数最小限度
    :param Z: 执行检测的次数
    '''
    G = (230, 230, 230)
    N = 1
    Z = 4
    for i in xrange(0, Z):
        for x in xrange(1, w - 1):
            for y in xrange(1, h - 1):
                nearDots = captcha.getNears(im, x, y, G)
                if nearDots < N:
                    im.putpixel((x, y), (255, 255, 255))

def reCount(countStr):
    p = r"^\d(.[-+]|[-+]|[-+].)\d"
    b = re.search(p, countStr)
    if b == None:
        return None
    else:
        countStr = b.group()
        if countStr[1:-1] == "++" or countStr[1:-1] == "+":
            count = int(countStr[0]) + int(countStr[-1])
        elif countStr[1:-1] == "--" or countStr[1:-1] == "-":
            count = int(countStr[0]) - int(countStr[-1])
        else:
            count = None
    return count

###############主流程函数###############
def get_image(cookies):
    try:
        url = 'http://gsxt.gzgs.gov.cn/search!generateCode.shtml?validTag=searchImageCode&'
        headers_info_2 = {
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Host': 'gsxt.gzgs.gov.cn',
            'Referer':'http://gsxt.gzgs.gov.cn/list.jsp',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
            'Connection': 'keep-alive'
        }
        CImages_html=Session.get(url=url,headers=headers_info_2,timeout = 5)
        file  = BytesIO(CImages_html.content)
        im = Image.open(file)
        return im
    except:
        return None
        # get_image(cookies)

def getCount(im, prName):
    count = 0
    squares = {
        5: [32, 70, 108, 146, 184, 222],
        6: [34, 65, 96, 128, 159, 190, 222],
        7: [32, 60, 87, 114, 141, 169, 197, 225]
    }
    w, h = im.size
    sKey = getBoxs(im, w, h)
    imBoxs = []
    for i in range(len(squares[sKey]) - 1):
        box = (squares[sKey][i], 11, squares[sKey][i + 1], 38)
        im_box = im.crop(box)
        w, h = im_box.size
        H0, C0 = getMainColor(im_box, w, h)
        delLines(im_box, w, h, H0, C0)
        im_box = captcha.highlight(im_box, w, h, 5)
        imBoxs.append(im_box)
    w_format = 38
    h_format = 27
    countStr = captcha.boxs2countStr(imBoxs, w_format, h_format, prName)
    count = reCount(countStr)
    return count

def get_html(company_name, count):
    url = "http://gsxt.gzgs.gov.cn/query!searchSczt.shtml"
    headers_info = {
                    'Accept-Encoding': 'gzip, deflate',
                    'Connection': 'keep-alive',
                    'Host': 'gsxt.gzgs.gov.cn',
                    'Referer': 'http://gsxt.gzgs.gov.cn/list.jsp',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
                }
    data = {
            'q': company_name,
            'validCode': count
            }
    req = Session.post(url=url, headers=headers_info,data=data,timeout=10)
    jsonA = json.loads(req.content)#req.text是乱码的
    return jsonA

def append_list(jsonA):
    url_list = []
    info = jsonA["data"]
    if info != []:
        for i in info:#k,qylx,searchT
            tag_nbxh = i["nbxh"]
            tag_ztlx = i["ztlx"]
            tag_qymc = i["qymc"]
            tag_zch = i["zch"]
            url_list.append([tag_nbxh, tag_ztlx, tag_qymc, tag_zch])
    return url_list

def main(**kwargs):
    global F_guizhou_query
    F_guizhou_query = F_guizhou_query - 1
    if F_guizhou_query < 0 :
        raise Exception("网站挂啦！！！>..<")
    name = kwargs.get('name')
    prName = "f3_guizhou"
    cookies = {'JSESSIONID':'0000dTRJoou3-cXGhEt8xZTJNma:-1', 'hbgjs':'52705030'}
    im = get_image(cookies)
    if im == None:
        return main(name=name)
    else:
        count = getCount(im, prName)
        if count==None:
            return main(name=name)
        else:
            jsonA = get_html(name, count)
            if jsonA.has_key("data")==False:
                return main(name=name)
            else:
                url_list = append_list(jsonA)
        return url_list

# for i in range(0,1):
#     name = '融金所'
#     url_list = main(name)
#     print url_list
if __name__ == "__main__":
    namelist = [
        '经开区杨氏尖椒鸡店',
    ]
    print main(name = namelist)
    # for name in namelist:
    #     url_list = main(name)
    #     if len(url_list)>0:
    #         print "tag_list = '%s',#%s"%(str(url_list[0][0]),name)
    #         time.sleep(15)