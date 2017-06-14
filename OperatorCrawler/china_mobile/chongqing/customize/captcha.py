# -*- coding:utf-8 -*-
"""
    用于验证码处理与识别的一系列操作

    @author：H2OSIR

    Functions：
        download_image  下载图片
        twoValueImage   二值图对象 return：image
        two_Value       将二值图转换为对应的二值数组、字典、列表，默认是dict
        clear_frame     清除边框
        clear_dots      清除噪点
        clear_noise     利用自定义矩形框来清除大块的噪点
        clear_lines     清除干扰线 （可优化）
        format_size     重定义图片大小
        cut_mean        平均等分切割（最基础的正常切割）
        cut_around      环切
        distance        计算两个向量（数据点或样本）的欧式距离
        loadTrainSet    读取训练集.
        write_csv       将list写入csv
        classify_KNN    KNN算法识别验证码
        classify_SVM    SVM算法识别验证码（库的版本升级后有bug）

"""


from __future__ import unicode_literals
import csv
import sys
import operator
import numpy as np
import pandas as pd
from os import listdir
from PIL import Image
from io import BytesIO
from sklearn import svm
from sklearn.decomposition import PCA
from requests.sessions import Session


# 下载图片
def download_image(url, **kwargs):
    """下载验证码图片

    :param url: 验证码网址
    :param kwargs: requests的请求参数一致
    :return: image对象 or None
    """

    response = None
    times = 0
    while times < 10:
        try:
            session = Session()
            response = session.request(method='GET', url=url, **kwargs)
            break
        except:
            times += 1
            print 'Timeout, I will try to request again……'

    image = None
    if response != None:
        file = BytesIO(response.content)
        image = Image.open(file)

    return image

# 二值图对象
def twoValueImage(image, G, background='white'):
    """将图像变黑白

    :param image: Image对象
    :param G: 阈值
    :param background 背景颜色， 默认为白色
    :return: Image对象
    """

    # 转成灰度图
    image = image.convert('L')

    for y in xrange(0, image.size[1]):
        for x in xrange(0, image.size[0]):
            g = image.getpixel((x, y))
            if background == 'white':
                if g > G:
                    image.putpixel((x, y), 255)
                else:
                    image.putpixel((x, y), 0)
            else:
                if g > G:
                    image.putpixel((x, y), 0)
                else:
                    image.putpixel((x, y), 255)

    return image

# 将二值图转换为对应的二值数组、字典、列表，默认是dict
def two_Value(image, type='dict'):
    """将二值图转换为对应的二值数组、字典、列表，默认是dict

    :param image: Image对象
    :param type: 二值后返回值的类型，list 、dict or array
    :return: type型数据
    """
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

# 清除边框
def clear_frame(image, n=1, background='white'):
    """清除边缘噪点，

    :param image:
    :param n: 多少个像素点的边框
    :param background: 默认白色背景
    :return:
    """

    image = image.convert('L')  # black is 0, white is 255
    if background != 'white':
        back_value = 0
    else:
        back_value = 255
    for y in range(0, image.size[1]):
        for x in range(0, image.size[0]):
            if x < n or x >= image.size[0] - n:
                image.putpixel((x, y), back_value)
                continue
            if y < n or y >= image.size[1] - n:
                image.putpixel((x, y), back_value)
                continue

    return image

# 清除噪点
def clear_dots(image, dots=1, N=1):
    """清除噪点  clear noise dots

    :param dots: number for near dots
    :param N: clear times
    :return: image
    """

    image = image.convert('L')  # black is 0, white is 255

    image = clear_frame(image)

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

                if nearDots < dots:
                    image.putpixel((x, y), 255)

    return image

# 利用自定义矩形框来清除大块的噪点
def clear_noise(image, size):
    """利用自定义矩形框清除噪点

    :param image: 二值图
    :param size: 自定义矩形框的大小  type: tuple
    :return: image
    """

    image = image.convert('L')
    for y in range(image.size[1] - size[1]):
        for x in range(image.size[0] - size[0]):
            white = True
            for xx in range(x, x + size[0]):
                if xx == x or xx == x + size[0] - 1:
                    for yy in range(y, y + size[1]):
                        if image.getpixel((xx, yy)) != 255:
                            white = False
                            break
                else:
                    if (image.getpixel((xx, y)) != 255 or
                                image.getpixel((xx, y + size[1] -1)) != 255):
                        white = False
                        break
            if white:
                for i in range(x, x + size[0]):
                    for j in range(y, y + size[1]):
                        image.putpixel((i, j), 255)

    return image

# 清除干扰线 （可优化）
def clear_lines(black_white_image):
    """清除单像素点干扰线

    原理：上下两个点或左右两个点为异色，则该点属于干扰线的点

    :param black_white_image: 黑白二值图
    :return: image
    """

    for x in range(1, black_white_image.size[0] - 1):
        for y in range(1, black_white_image.size[1] - 1):
            pix = black_white_image.getpixel((x, y))
            pix_up = black_white_image.getpixel((x, y - 1))
            pix_down = black_white_image.getpixel((x, y + 1))
            pix_left = black_white_image.getpixel((x - 1, y))
            pix_right = black_white_image.getpixel((x + 1, y))
            if pix != pix_up and pix != pix_down:
                black_white_image.putpixel((x, y), 255)
            elif pix != pix_left and pix != pix_right:
                black_white_image.putpixel((x, y), 255)

    return black_white_image

# 重定义图片大小
def format_size(image, new_size):
    """
    :param image: Image对象
    :param new_size: 新的尺寸, tuple or list [width, height] or (width, height)
    :return: Image对象
    """

    # image_dict: 来自于twoValue的。使用前图片需做二值化处理,new_size is tuple。
    image_dict = two_Value(image, 'dict')
    img = Image.new("1", (new_size[0], new_size[1]))

    for x in xrange(0, new_size[0]):
        for y in xrange(0, new_size[1]):
            if image.size[0] < new_size[0]:
                x0 = x - abs(new_size[0] - image.size[0]) // 2
            else:
                x0 = x + abs(new_size[0] - image.size[0]) // 2
            if image.size[1] < new_size[1]:
                y0 = y - abs(new_size[1] - image.size[1]) // 2
            else:
                y0 = y + abs(new_size[1] - image.size[1]) // 2
            if image_dict.has_key((x0, y0)):
                img.putpixel((x, y), image_dict[(x0, y0)])
            else:
                img.putpixel((x, y), 1)

    return img

# 环切
def cut_around(image):
    """将二值对象环切

    :param image: 二值Image对象
    :return: 二值Image对象
    """

    x1 = 0
    x2 = image.size[0]
    y1 = 0
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

# 平均切割
def cut_mean(image, count=4):
    """平均切割方法

    :param image: 带切割图， Image对象
    :param count: 切割的块数，默认切 4 块
    :return: Image list
    """

    w, h = image.size
    union = (w + 1) / count
    images = []
    for i in range(count):
        img = image.crop((0 + union * i, 0, union * (i + 1), h))
        images.append(img)

    # 切掉最后一张图右边的黑边
    p = union * count - w   # 黑边的宽
    images[-1] = images[-1].crop((0, 0,
                                  images[-1].size[0] - p, images[-1].size[1]))

    return images   # 几张图可能大小不一致

# 计算距离
def distance(array1, array2, axis=None):
    """计算两个数组矩阵的欧式距离;

    axis=0，求每列的
    axis=1，求每行的
    """

    # distance = (np.sum((array1 - array2), axis)** 2) ** 0.5
    distance = np.sqrt(np.sum(np.power(array1 - array2, 2)))

    return distance

# 生成csv训练集
def create_train_data(directory, file=None):
    """将已标注好的图片训练集生产csv

    :param directory: 图片训练集的文件夹目录
    :return: None 保存csv, 调用该函数的脚本目录
    """
    if directory[-1] != '/':
        directory = directory + '/'
    if not file:
        file = sys.path[0] + '/'
    elif file[-1] != '/':
        file = file + '/'
    list = listdir(directory)
    for each in list:
        row = []
        row.append(each[0])     # add  label
        img = Image.open(directory + each)
        train_x = two_Value(img, 'list')
        row.extend(train_x)
        write_csv(file + 'train_data.csv', row)

# 读取训练集
def loadTrainSet(fileName):
    """该函数读取加载训练集

    :param fileName: 训练集所在路径，csv文件，第一列为label，每行是一个样本
    :return: labels or trainX
    """

    # 如果路径中不存在 . ，则属于读取图片的训练集，否则是读取csv
    if '.csv' not in fileName:
        train_data = listdir(fileName)
        labels = []
        trains = []
        for i in range(len(train_data)):
            image = Image.open(fileName + train_data[i])
            array = two_Value(image, 'list')
            trains.append(array)
            labels.append(train_data[i][0])
        trains = np.array(trains)
        labels = np.array(labels)
    else:
        train = pd.read_csv(fileName)
        trains = train.values[:, 1:]
        labels = train.ix[:, 0]

    return trains, labels

# 将list写入csv
def write_csv(fileName, values):
    """以追加的方式将list数据写入csv文件

    :param fileName: file path
    :param values: type is list
    :return: 无返回值
    """

    with open(fileName, 'ab') as file:
        csv_file = csv.writer(file)
        csv_file.writerow(values)

# KNN分类
def classify_KNN(image, trains, labels, k):
    '''KNN'''
    unArray = two_Value(image, 'list')
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

    image_array = two_Value(image, 'list')
    obj_array = np.array(image_array)
    obj_array = pca.transform(obj_array)
    obj_string = svc.predict(obj_array)

    return obj_string[0]

if __name__ == '__main__':

    img = Image.open('example/01/6bbz.png')

    img = twoValueImage(img, 100)

    img = clear_frame(img, 2)

    img = clear_noise(img, (4, 4))

    # # img.save('test.png')
    # img.show()
    images = cut_mean(img, 4)

    for i, each in enumerate(images):
        images[i] = format_size(each, (25, 25))
    for i, each in enumerate(images):
        each.save('%s.png' % str(i))




