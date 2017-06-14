# -*- coding:utf-8 -*-
import conf
import time
import os,os.path
from os import listdir
import glob
import csv
import pandas as pd
import numpy as np
import operator
from sklearn.decomposition import PCA
from sklearn import svm
from difflib import SequenceMatcher
import pytesseract
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageDraw
pca = PCA(n_components=0.8, whiten=True)
svc = svm.SVC(kernel='rbf', C=10)

if os.path.exists(conf.ImgBaseDir) == False:
    os.mkdir(conf.ImgBaseDir)

# 将二值图转换为对应的二值数组、字典、列表，默认是dict
def twoValue(image, type='dict'):
    '''
    :param image: Image对象
    :param type: 二值后返回值的类型，list 、dict or array
    :return: type型数据
    '''
    from numpy import zeros
    types = {
        'dict': {},
        'array': zeros((image.size[1], image.size[0]), dtype=int),
        'list': []
    }

    img_value = types[type]

    for y in xrange(0, image.size[1]):
        for x in xrange(0, image.size[0]):
            g = image.getpixel((x, y))
            if g <> 0:
                if type == 'dict':
                    img_value[(x, y)] = 1
                elif type == 'array':
                    img_value[y][x] = 1
                else:
                    img_value.append(1)
            else:
                if type == 'dict':
                    img_value[(x, y)] = 0
                elif type == 'array':
                    img_value[y][x] = 0
                else:
                    img_value.append(0)

    return img_value

# 二值图对象
def twoValueImage(image, G, background='white'):
    '''
    :param image: Image对象
    :param G: 阈值
    :param background 背景颜色， 默认为白色
    :return: Image对象
    '''
    # 图转二值
    image = image.convert('L')
    t2val = {}
    for y in xrange(0, image.size[1]):
        for x in xrange(0, image.size[0]):
            g = image.getpixel((x, y))
            if background == 'white':
                if g > G:
                    t2val[(x, y)] = 1
                else:
                    t2val[(x, y)] = 0
            else:
                if g > G:
                    t2val[(x, y)] = 0
                else:
                    t2val[(x, y)] = 1

    # 二值转图
    image = Image.new("1", image.size)
    draw = ImageDraw.Draw(image)

    for x in xrange(0, image.size[0]):
        for y in xrange(0, image.size[1]):
            draw.point((x, y), t2val[(x, y)])

    return image

# 去噪点
def clear(image, C=1, N=1):
    '''
    :param image: twoValues Image Object
    :param C: counts of around
    :param N: times of clear
    :return: image object
    '''
    image = image.convert('L')  # black is 0, white is 255
    # 去边框
    for y in range(0, image.size[1]):
        for x in range(0, image.size[0]):
            if x == 0 or x == image.size[0] - 1:
                image.putpixel((x, y), 255)
                continue
            if y == 0 or y == image.size[1] - 1:
                image.putpixel((x, y), 255)
                continue
    for i in range(0, N):
        for y in range(1, image.size[1] - 1):
            for x in range(1, image.size[0] - 1):
                nearDots = 0
                d = image.getpixel((x, y))  # 中心点的灰度值
                if d == image.getpixel((x - 1, y - 1)):
                    nearDots += 1
                if d == image.getpixel((x, y - 1)):
                    nearDots += 1
                if d == image.getpixel((x + 1, y - 1)):
                    nearDots += 1
                if d == image.getpixel((x - 1, y)):
                    nearDots += 1
                if d == image.getpixel((x + 1, y)):
                    nearDots += 1
                if d == image.getpixel((x - 1, y + 1)):
                    nearDots += 1
                if d == image.getpixel((x, y + 1)):
                    nearDots += 1
                if d == image.getpixel((x + 1, y + 1)):
                    nearDots += 1

                if nearDots < C:

                    image.putpixel((x, y), 255)


    return image

# 将二值对象环切
def cutAround(image):
    '''
    :param image: 二值Image对象
    :return: 二值Image对象
    '''
    x1 = 0
    y1 = 0
    x2 = image.size[0]
    y2 = image.size[1]
    # 右移
    for x in range(image.size[0]):
        # 下移
        for y in range(image.size[1]):
            color = image.getpixel((x,y))
            if color == 0:       # 发现不是白色就停
                x1 = x           # 返回第一条竖线的x值
                break
            else:
                continue
        else:
            continue
        break

    # 左移
    for x in range(image.size[0]-1, -1, -1):
        # 下移
        for y in range(image.size[1]):
            color = image.getpixel((x, y))
            if color == 0:            # 发现不是白色就停
                x2 = x + 1            # 返回第一条竖线的x值
                break
            else:
                continue
        else:
            continue
        break

    # 下移
    for y in range(image.size[1]):
        # 右移
        for x in range(image.size[0]):
            color = image.getpixel((x, y))
            if color == 0:  # 发现不是白色就停
                y1 = y      # 返回第一条横线的y值
                break
            else:
                continue
        else:
            continue
        break

    # 上移
    for y in range(image.size[1]-1, -1, -1):
        # 右移
        for x in range(image.size[0]):
            color = image.getpixel((x, y))
            if color == 0:  # 发现不是白色就停
                y2 = y + 1     # 返回第一条横线的y值
                break
            else:
                continue
        else:
            continue
        break

    image = image.crop((x1, y1, x2, y2))

    return image

# 将图片按目标尺寸格式化，不足的填充白色
def formatImg(image, new_size):
    '''
    :param image: Image对象
    :param new_size: 新的尺寸
    :return: Image对象
    '''
    # image_dict: 来自于twoValue的。使用前图片需做二值化处理,new_size is tuple。
    image_dict = twoValue(image, 'dict')
    im = Image.new("1",(new_size[0],new_size[1]))
    draw = ImageDraw.Draw(im)
    for x in xrange(0,new_size[0]):
        for y in xrange(0,new_size[1]):
            if image.size[0] < new_size[0]:
                x0 = x-abs(new_size[0]-image.size[0])//2
            else:
                x0 = x+abs(new_size[0]-image.size[0])//2
            if image.size[1] < new_size[1]:
                y0 = y-abs(new_size[1]-image.size[1])//2
            else:
                y0 = y+abs(new_size[1]-image.size[1])//2
            if image_dict.has_key((x0,y0)):
                im.putpixel((x,y),image_dict[(x0,y0)])
            else:
                im.putpixel((x, y), 1)
    return im

# 计算距离
def distance(array1, array2, axis=None):
    '''计算两个数组矩阵的欧式距离;
    axis=0，求每列的
    axis=1，求每行的'''
    distance = (np.sum((array1 - array2), axis) ** 2) ** 0.5

    return distance

# 读取训练集
def loadTrainSet(path):
    '''
    该函数读取加载训练集
    :param csv_path: 训练集所在路径，csv文件，第一列为label，每行是一个样本
    :return: labels or trainX
    '''
    if '.csv' not in path:
        train_data = listdir(path)
        labels = []
        trains = []
        for i in range(len(train_data)):
            image = Image.open(path + train_data[i])
            array = twoValue(image, 'list')
            trains.append(array)
            labels.append(train_data[i][0])
        trains = np.array(trains)
        labels = np.array(labels)
    else:
        train = pd.read_csv(path)
        trains = train.values[:, 1:]
        labels = train.ix[:, 0]

    return trains, labels

# KNN分类
def classify_KNN(image, trains, labels, k):
    '''KNN'''
    unArray = twoValue(image, 'list')
    unArray = np.array(unArray) # 转换成一维数组
    diff = []

    # 依次计算距离
    for each in trains:
        dis = distance(unArray, each)
        diff.append(dis)

    # 统计距离最小的个数， 将diff与labels转换成array
    diff = np.array(diff)
    # labels = np.array(labels)

    # 排序后的数据在原数据中的下标
    index = np.argsort(diff)

    # 统计标签的个数
    count = {}
    for i in range(5):
        votelabel = labels[index[i]]
        count[votelabel] = count.get(votelabel, 0) + 1

    # 按Count字典的第2个元素（即类别出现的次数）从大到小排序
    sortedCount = sorted(count.items(), key=operator.itemgetter(1), reverse=True)

    return sortedCount[0][0]

# SVM分类
def classify_SVM(image, train_x, train_y):

    # 都是array，每个样本的唯独与image都是一维数组
    pca = PCA(n_components=0.8, whiten=True)
    svc = svm.SVC(kernel='rbf', C=10)

    train_x = pca.fit_transform(train_x)
    svc.fit(train_x, train_y)

    image_array = twoValue(image, 'list')
    obj_array = np.array(image_array)
    obj_array = pca.transform(obj_array)
    obj_string = svc.predict(obj_array)

    return obj_string[0]

######## kexh_common ########
# Part_1 for(pytesseract法): e2_hubei,b1_liaoning,e1_henan,d2_guangxi,c4_anhui,f1_chongqing...
def replaceStr(s):
    dict = {
        ',': '',
        '、': '',
        '~': '',
        '，': '',
        "'": '',
        'v': '',
        '右口': '',
        '\\': '一',
        '夭': '天',
        '又寸': '对',
        '白勺': '的',
        '女子': '好',
        '弓虽': '强',
        'i炎': '谈',
        '7咸': '减',
        '}咸': '减',
        ')咸': '减',
        '7曦': '减',
        '歹威': '减',
        '歹咸': '减',
        '〉咸': '减',
        '歹属贡': '减',
        '町口': '加',
        '刃口': '加',
        '力口': '加',
        '刀口': '加',
        'o': '0',
        'l': '1',
        'Z': '2',
            }
    for d in dict:
        s = s.replace(d, dict[d])
    return s

def get_string(im):
    with open(conf.dictoryPath, 'r') as f3:
        dictory = f3.readlines()
    w,h = im.size
    for x in range(w):
        for y in range(h):
            pixel = im.getpixel((x,y))
            if sum(pixel)/3 > 225:
                im.putpixel((x,y), (0,0,0))
            else:
                im.putpixel((x,y), (255,255,255))
    # 下面这段还可以优化一下
    string = pytesseract.image_to_string(im, lang='chi_sim',config ='-psm 7').strip()
    string = replaceStr(string)
    rank_dic = {}
    for a in dictory:
        a = a.replace('\n', '')
        ratio = SequenceMatcher(None, a, string).ratio()
        if ratio > 0:
            rank_dic[a] = ratio
    string = max(rank_dic.items(), key=operator.itemgetter(1))[0]
    return string

# Part_2 for（svm法）: c7_shandong,c6_jiangxi,g5_xinjiang,b2_jilin,g3_qinghai,f3_guizhou...
def formatImg_2(w_format, h_format, image_array, w, h):
    # image_array: 来自于twoValue_2的。使用前图片需做二值化处理。
    im = Image.new("1",(w_format,h_format))
    draw = ImageDraw.Draw(im)
    for x in xrange(0,w_format):
        for y in xrange(0,h_format):
            if w < w_format:
                x0 = x-abs(w_format-w)//2
            else:
                x0 = x+abs(w_format-w)//2
            if h < h_format:
                y0 = y-abs(h_format-h)//2
            else:
                y0 = y+abs(h_format-h)//2
            if image_array.has_key((x0,y0)):
                im.putpixel((x,y),image_array[(x0,y0)])
            else:
                im.putpixel((x, y), 1)
    return im

def parse(train_x, train_y, image_array):
    obj_array = np.array(image_array)
    train_x = pca.fit_transform(train_x)
    obj_array = pca.transform(obj_array)
    svc.fit(train_x, train_y)
    obj_string = svc.predict(obj_array)
    return obj_string

def twoValue_0(im, G, image_array):
    w, h = im.size
    for x in xrange(0, w):
        for y in xrange(0, h):
            g = im.getpixel((x, y))
            if g > G:
                image_array.append(0)
            else:
                image_array.append(1)
    return image_array

def twoValue_1(im, G):
    w, h = im.size
    imageList = []
    for x in xrange(0, w):
        image_col = []
        for y in xrange(0, h):
            g = im.getpixel((x, y))
            if g > G:
                image_col.append(0)
            else:
                image_col.append(1)
        imageList.append(image_col)
    image_array = np.array(imageList)
    return image_array

def twoValue_2(im, G):
    image_array = {}
    w, h = im.size
    for x in xrange(0, w):
        for y in xrange(0, h):
            g = im.getpixel((x, y))
            if g > G:
                image_array[(x, y)] = 1
            else:
                image_array[(x, y)] = 0
    return image_array

def getNears(im, x, y, G):
    nearDots = 0
    if im.getpixel((x - 1, y - 1)) < G:
        nearDots += 1
    if im.getpixel((x - 1, y)) < G:
        nearDots += 2
    if im.getpixel((x - 1, y + 1)) < G:
        nearDots += 1
    if im.getpixel((x, y - 1)) < G:
        nearDots += 1
    if im.getpixel((x, y + 1)) < G:
        nearDots += 1
    if im.getpixel((x + 1, y - 1)) < G:
        nearDots += 1
    if im.getpixel((x + 1, y)) < G:
        nearDots += 2
    if im.getpixel((x + 1, y + 1)) < G:
        nearDots += 1
    return nearDots

def highlight(im, w, h, Z):
    '''去孤立点部分，当小于N时，无论中心点是什么颜色，都会被置为白色；如果中心点原先为白色，大于N的话，一样跳过.

    :param w: 判定临近点是否算有颜色的基准值
    :param h: 有颜色的临近点个数最小限度
    :param Z: 执行检测的次数
    '''
    G = (230,230,230)
    N = 1
    Z = 5
    for i in xrange(0, Z):
        for x in xrange(1, w-1):
            for y in xrange(1, h-1):
                nearDots = getNears(im, x, y, G)
                if nearDots < N:
                    im.putpixel((x,y), (255,255,255))
    enhancer = ImageEnhance.Contrast(im)
    im = enhancer.enhance(150)
    im = im.convert('1')  # 二值化
    return im

def boxs2countStr(imBoxs, w_format, h_format, prName):
    '''
    将切好的文字格识别成一个字符串。目前做法是先统一大小并保存到ImgPath，再调取parse得到比对结果。
    调用它的：getCount(im, prName)。
    '''
    ImgList = []
    timestr = time.strftime('%Y-%m-%d_%H-%M-%S')
    ImgDir = os.path.join(conf.ImgBaseDir,prName+"_img\\",)
    csvPath = os.path.join(conf.csvDir,prName+"_train_operator.csv")
    if os.path.exists(ImgDir)==False:
        os.mkdir(ImgDir)
    for m, im in enumerate(imBoxs):
        w, h = im.size
        im = im.convert('1')  # 二值化
        image_array = twoValue_2(im, 100)
        im = formatImg_2(w_format, h_format, image_array, w, h)
        ImgPath = ImgDir + timestr + "_" + str(m + 1) + ".jpg"
        im.save(ImgPath)
        ImgList.append(ImgPath)
    train = pd.read_csv(csvPath, low_memory=False)
    train_x = train.values[:, 1:]
    train_y = train.ix[:, 0]
    countStr = ''
    for n,ImgPath in enumerate(ImgList):
        im = Image.open(ImgPath)
        im = im.convert("1")
        image_array = twoValue_0(im, 100, [])
        obj_string = parse(train_x, train_y, image_array)
        obj_string = str(obj_string[0])
        countStr = countStr+obj_string
    rm_cache_img(prName)
    return countStr

def rm_cache_img(prName):
    ImgDir = os.path.join(conf.ImgBaseDir,prName+"_img",)
    for i in glob.glob(ImgDir+"*.jpg"):
        if os.path.exists(i):
            os.remove(i)

def tocsv_n_os(ImgDir, a, csvPath):
    '''
    这个函数只用于样本扩充的情况下，平常不用用到。
    Part A是将各个子文件夹（名称见列表a）的图片处理成数据放到excel中；
    Part B是根据excel的数据，判断一张图切分后的各个文字格图片要放到什么子文件夹中。
    各参数格式如下：
    ImgDir = "F:\\material\\cache_shandong_Img\\"
    a = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0', '+', '-', 'cheng', 'kongge']
    csvPath = "F:\\material\\cache_shandong_Img\\train_opeator.csv"
    '''
    # # [Part A]
    for k in a:
        kindPath = ImgDir + k + "\\"
        for i in glob.glob(kindPath+"*.jpg"):
            # print i
            im = Image.open(i).convert('1')
            image_array = twoValue_0(im, 100, [k])
            # print image_array
            resultFile = open(csvPath, 'ab')
            wr = csv.writer(resultFile)
            wr.writerow(image_array)
            time.sleep(0.06)
    # [Part B]
    # train = pd.read_csv(csvPath)
    # train_x = train.values[:, 1:]
    # train_y = train.ix[:, 0]
    # for i in glob.glob(ImgDir + "forCheck\\"+"*.jpg"):
    #     im = Image.open(i)
    #     w, h = im.size
    #     if w < 50:
    #         im = im.convert("1")
    #         image_array = twoValue_0(im, 100, [])
    #         obj_string = parse(train_x, train_y, image_array)
    #         obj_string = str(obj_string[0])
    #         # print ImgDir+obj_string+"\\"
    #         if os.path.exists(ImgDir+obj_string+"\\")==True:
    #             newPath = oj(ImgDir+obj_string+"\\", os.path.split(i)[1])
    #             # print newPath
    #             shutil.copy(i,newPath)

# nearest_cluster_center
# guizhou