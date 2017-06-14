# -*- coding:utf-8 -*-
"""
author: liuyd
update_date: 2017/01/03
"""
from __future__ import unicode_literals
import pandas as pd
import numpy as np
import operator
from sklearn.decomposition import PCA
from sklearn import svm
from os import listdir
from io import BytesIO
from PIL import Image,ImageDraw
import requests
from pytesseract import image_to_string
import csv
import os

cur_dir=os.path.dirname(__file__)


#下载验证码
def load_image(url,**kwargs):
    """

    :param url: 验证码的url
    :param kwargs: 获取验证码的参数
    :return: image对象
    """
    pass

#将训练集写入CSV
def write_csv(path,data):
    """
    将List数据写入csv文件
    :param path:
    :param data:
    :return:
    """
    with open(path,'ab') as file:
        csv_file=csv.writer(file)
        csv_file.writerow(data)
    print "数据写入完成"

#必须是二值图转二值数据值，图片必须是经过处理的
def twoValue(image,type='list'):
    """

    :param image:
    :param type: 二值后返回的类型，list,dict,tuple
    :return: type数据
    """
    from numpy import zeros
    types={
        'dict':{},
        'array':zeros((image.size[1],image.size[0]),dtype=int),
        'list':[]
    }
    image_value=types[type]
    for y in xrange(0,image.size[1]):
        for x in xrange(0,image.size[0]):
            g=image.getpixel((x,y))
            if g<>0:
                if type=="dict":
                    image_value[y][x]=1
                elif type=='array':
                    image_value[y][x]=1
                else:
                    image_value.append(1)
            else:
                if type=="dict":
                    image_value[y][x]=0
                elif type=='array':
                    image_value[y][x]=0
                else:
                    image_value.append(0)
    return image_value

#获取二值图对象
def twoValueImage(image,G,background='white'):
    """

    :param image: image对象
    :param G: 閥值
    :param background: 背景颜色
    :return: Image对象
    """
    image=image.convert("L")
    t2val={}
    for y in xrange(0,image.size[1]):
        for x in xrange(0,image.size[0]):
            g=image.getpixel((x,y))
            if background=="white":
                if g>G:
                    t2val[(x,y)]=1
                else:
                    t2val[(x,y)]=0
            else:
                if g>G:
                    t2val[(x,y)]=0
                else:
                    t2val[(x,y)]=1
    image=Image.new("1",image.size)
    draw=ImageDraw.Draw(image)

    for x in xrange(0,image.size[0]):
        for y in xrange(0,image.size[1]):
            draw.point((x,y),t2val[(x,y)])
    return image


#去噪点
def clear(image,C=1,N=1):
    """

    :param image: twoValues Image Object
    :param C: counts of around
    :param N: times of clear
    :return: image object
    """
    image=image.convert("L")
    #去边框
    for y in range(0,image.size[1]):
        for x in range(0,image.size[0]):
            if x ==0 or x==image.size[0]-1:
                image.putpixel((x,y),255)
                continue
            if y==0 or y==image.size[1]-1:
                image.putpixel((x,y),255)
                continue

    #去中间图片的噪点
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

#将而知二值对象进行环切
def cutAround(image):
    """

    :param image:二值Image对象
    :return:环切后的二值Image对象
    """
    x1,y1,x2,y2=0,0,1,1
    #右移
    a1=False
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            color=image.getpixel((x,y))
            if color==0:
                x1=x
                a1=True
                break
            else:
                continue
        if a1==True:
            break

    #左移
    a2=False
    for x in range(image.size[0]-1,-1,-1):
        for y in range(image.size[1]):
            color=image.getpixel((x,y))
            if color==0:
                x2=x+1
                a2=True
                break
        if a2==True:
            break
    #下移
    b1=False
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            color=image.getpixel((x,y))
            if color==0:
                y1=y
                b1=True
                break
            else:
                continue
        if b1==True:
            break
#上移
    b2=False
    for y in range(image.size[1]-1,-1,-1):
        for x in range(image.size[0]):
            color=image.getpixel((x,y))
            if color==0:
                y2=y+1
                b2=True
                break
            else:
                continue
        if b2==True:
            break
    image=image.crop((x1,y1,x2,y2))
    return image

def main():
    image=Image.open('2.png')
    im=twoValueImage(image,120)
    cutAround(im).show()


main()



























