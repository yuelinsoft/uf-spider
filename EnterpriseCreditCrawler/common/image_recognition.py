#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals, print_function

"""
    image_recognition
    ~~~~~~~~~

    用以图像（验证码）处理和识别

    :copyright: (c) 2017 by cds@uf-club.
    :license: MIT, see LICENSE for more details.
"""

__versions__ = '1.0.0'

import matplotlib.pyplot as plt
import numpy as np
import pytesseract
import requests
import skimage.filters.rank as sfr

from StringIO import StringIO
from PIL import Image
from skimage import (morphology, io, feature, filters, exposure, color,
                     restoration)

ROW_RANGE_LIST = [(0, 30), (31, 70), (71, 110), (111, 150)]
COLUMN_RANGE_LIST = [(0, 50), (0, 50), (0, 50), (0, 50)]
CHR_LIST = range(97, 123) + range(48, 58) + range(65, 91)
SLICE_MAP = {'0101': {'fir_num': (0, 18),
                      'op': (17, 40),
                      'sec_num': (40, 56)
                      },
             '0111': {'fir_num': (0, 18),
                      'op': (17, 40),
                      'sec_num_1': (40, 53),
                      'sec_num_2': (53, 67)
                      },
             '1101': {'fir_num_1': (0, 18),
                      'fir_num_2': (17, 32),
                      'op': (30, 53),
                      'sec_num': (53, 67)
                      },
             '1111': {'fir_num_1': (0, 18),
                      'fir_num_2': (17, 32),
                      'op': (30, 53),
                      'sec_num_1': (53, 67),
                      'sec_num_2': (65, 78)
                      },
             }
ADD_LIST = ['加', '伽', '‖', '"']
SUB_LIST = ['乘', '…', ]


def yunnan_check_code_processing(img):
    """对于云南验证码的处理

    :param img: 云南验证码图片（灰度图）
    :return: 二值化后的验证码图片
    """
    dilation_img = morphology.dilation(img, morphology.disk(1))
    erosion_img = morphology.erosion(dilation_img, morphology.disk(1))
    gaussian_img = filters.gaussian(erosion_img, sigma=1.5)
    dilation2_img = morphology.dilation(gaussian_img, morphology.disk(2))
    thresh = filters.threshold_otsu(dilation2_img)
    bin_img = (dilation2_img >= thresh) * 1.0
    return [bin_img]


def shanghai_chunk_code_processing(img, row_range, column_range):
    """对于上海分割验证码的处理

    :param img: 上海验证码分割后的图片
    :param row_range: 分割的横坐标范围
    :param column_range: 分割的纵坐标范围
    :return: 二值化后的分割验证码图片
    """
    img = img[column_range[0]: column_range[1], row_range[0]: row_range[1]]
    img = sfr.enhance_contrast(img, morphology.selem.disk(1))
    img = sfr.maximum(img, morphology.selem.rectangle(3, 2))
    img = morphology.dilation(img, morphology.selem.rectangle(2, 1))
    thresh = filters.threshold_otsu(img)
    img = (img >= thresh) * 1.0
    return img


def shanghai_check_code_processing(img):
    """对于上海验证码的处理

    :param img: 上海验证码图片（灰度图）
    :return: 二值化后的验证码图片
    """
    # img = exposure.adjust_gamma(img, gamma=2)
    img = morphology.dilation(img, morphology.selem.square(2))
    img = morphology.erosion(img, morphology.selem.square(3))
    bin_img = list()
    for i in range(4):
        chuck_img = shanghai_chunk_code_processing(img, ROW_RANGE_LIST[i],
                                                   COLUMN_RANGE_LIST[i])
        bin_img.append(chuck_img)
    return bin_img


def hebei_chunk_code_processing(img, row_range, column_range):
    """对于河北分割验证码的处理

    :param img: 河北验证码分割后的图片
    :param row_range: 分割的横坐标范围
    :param column_range: 分割的纵坐标范围
    :return: 二值化后的分割验证码图片
    """
    img = img[column_range[0]: column_range[1], row_range[0]: row_range[1]]
    img = sfr.enhance_contrast(img, morphology.selem.disk(1))
    img = sfr.maximum(img, morphology.selem.rectangle(3, 2))
    img = morphology.dilation(img, morphology.selem.rectangle(2, 1))
    # thresh = filters.threshold_otsu(img)
    # img = (img >= thresh) * 1.0
    img = morphology.remove_small_objects(img, 5)
    return img


def hebei_check_code_processing(img):
    """对于河北验证码的处理

    :param img: 河北验证码图片（灰度图）
    :return: 二值化后的验证码图片
    """
    img = exposure.adjust_gamma(img, gamma=2)
    img = morphology.dilation(img, morphology.selem.square(2))
    img = morphology.erosion(img, morphology.selem.square(3))
    bin_img = list()
    for i in range(4):
        chuck_img = hebei_chunk_code_processing(img, ROW_RANGE_LIST[i],
                                                COLUMN_RANGE_LIST[i])
        bin_img.append(chuck_img)
    return bin_img


def image_format(img):
    img = np.array(img.convert('L'))
    img = exposure.adjust_gamma(img, gamma=4)
    img = filters.median(img, morphology.selem.rectangle(1, 2))
    thresh = filters.threshold_otsu(img)
    img = (img >= thresh) * 1.0
    return img


def image_slicing(img, slice_map):
    slice_dict = dict()
    for slice_key in slice_map.keys():
        slice_dict.update({slice_key: Image.fromarray((img[0: 30,
                                                       slice_map[slice_key][0]:
                                                       slice_map[slice_key][1]]
                                                       * 255).astype(np.uint8))}
                          )
    return slice_dict


def slice_string(img_dict):
    img_str_dict = dict()
    for slice_key in img_dict.keys():
        if slice_key == 'op':
            img_str = pytesseract.image_to_string(img_dict[slice_key],
                                                  config='-psm 10 op',
                                                  lang='chi_sim')
        else:
            img_str = pytesseract.image_to_string(img_dict[slice_key],
                                   config='-psm 10 digit')
        if img_str:
            img_str_dict.update({slice_key: img_str})
        else:
            img_str_dict.update({slice_key: '8'})
    return img_str_dict


def str_operator(fir_num, op, sec_num):
    operator = op.decode('utf-8')
    if operator in ADD_LIST:
        try:
            return '{}'.format((int(fir_num) + int(sec_num)))
        except:
            return None
    elif operator in SUB_LIST:
        try:
            return '{}'.format(int(fir_num) * int(sec_num))
        except:
            return None
    else:
        return None


def img_show(raw_img, img_dict, title_dict):
    img_num = len(img_dict)
    plt.subplot(111 + img_num * 10)
    plt.title('raw img')
    plt.imshow(raw_img, plt.cm.gray)
    for i, img_key in enumerate(img_dict.keys()):
        plt.subplot(112 + img_num * 10 + i)
        plt.title(format(title_dict[img_key]).decode('utf-8'))
        plt.imshow(img_dict[img_key], plt.cm.gray)
    plt.show()


def shenzhen_check_code_processing(img, show=False):
    if img.size == (90, 30):
        img = image_format(img)
        img_flag = '0101'
        img_map = SLICE_MAP[img_flag]
        slice_dict = image_slicing(img, img_map)
        img_str_dict = slice_string(slice_dict)
        result = str_operator(img_str_dict['fir_num'], img_str_dict['op'],
                              img_str_dict['sec_num'])
    elif img.size == (105, 30):
        img = image_format(img)
        img_flag = '1101'
        img_map = SLICE_MAP[img_flag]
        slice_dict = image_slicing(img, img_map)
        img_str_dict = slice_string(slice_dict)
        first_num = img_str_dict['fir_num_1'] + img_str_dict['fir_num_2']
        result = str_operator(first_num, img_str_dict['op'],
                              img_str_dict['sec_num'])
        if not result:
            img_flag = '0111'
            img_map = SLICE_MAP[img_flag]
            slice_dict = image_slicing(img, img_map)
            img_str_dict = slice_string(slice_dict)
            second_num = img_str_dict['sec_num_1'] + img_str_dict['sec_num_2']
            result = str_operator(img_str_dict['fir_num'],
                                  img_str_dict['op'], second_num)
    elif img.size == (120, 30):
        img = image_format(img)
        img_flag = '1111'
        img_map = SLICE_MAP[img_flag]
        slice_dict = image_slicing(img, img_map)
        img_str_dict = slice_string(slice_dict)
        first_num = img_str_dict['fir_num_1'] + img_str_dict['fir_num_2']
        second_num = img_str_dict['sec_num_1'] + img_str_dict['sec_num_2']
        result = str_operator(first_num, img_str_dict['op'], second_num)
    else:
        result = None
    if show:
        img_show(img, slice_dict, img_str_dict)
    return result


def image_processing(img, province):
    """ 图像处理

    :param img: 原始图片
    :param province: 图片归属省份
    :param show: 是否展示
    :return: 处理后且二值化的图片
    """
    if province == 'yunnan':
        processing_img = yunnan_check_code_processing(img.convert('L'))
    elif province == 'shanghai':
        processing_img = shanghai_check_code_processing(img.convert('L'))
    elif province == 'hebei':
        # processing_img = hebei_check_code_processing(img.convert('L'))
        processing_img = hebei_check_code_processing(img)
    else:
        raise ValueError('请输入正确的省份名称')
    return processing_img


def image_ocr(img_array, config=None):
    """ 进行图像识别

    :param img: 二值化图片
    :param config: 附加 tesseract_ocr 命令
    :return: 识别的字符串，无法识别则为 None
    """
    ocr_str = list()
    for img in img_array:
        img = Image.fromarray((img * 255).astype(np.uint8))
        img_str = pytesseract.image_to_string(img, config=config)
        if img_str == None:
            return None
        else:
            ocr_str.append(img_str)
    ocr_str = ''.join(ocr_str)
    return ocr_str


def string_optimization(ocr_str):
    """ 字符串逻辑优化

    :param ocr_str: ocr 后得到的字符串
    :return: 优化后的字符串
    """
    if ocr_str != None:
        optimization_str = ''.join([_str for _str in ocr_str if ord(_str)in
                                    CHR_LIST])
        return None if len(optimization_str) != 4 else optimization_str
    else:
        return None


def image_recognition(raw_img, province, show=False, config=None):
    """ 对输入图片处理后进行识别，输出图片字符

    :param raw_img: 原始图像
    :param province: 图像归属省份
    :param show: 是否展示
    :param config: 附加 tesseract_ocr 命令
    :return: 优化后的 ocr 字符串，无法识别则为 None
    """
    if province == 'shenzhen':
        return shenzhen_check_code_processing(raw_img, show)
    processed_img = image_processing(raw_img, province)
    ocr_str = image_ocr(processed_img, config=config)
    optimization_str = string_optimization(ocr_str)
    if show:
        plt.subplot(111 + len(processed_img)*10)
        plt.title('raw img')
        plt.imshow(raw_img, plt.cm.gray)
        for i, img in enumerate(processed_img):
            plt.subplot(112 + len(processed_img)*10 + i)
            plt.title('processed img')
            plt.imshow(processed_img[i], plt.cm.gray)
        plt.show()
    return optimization_str


if __name__ == '__main__':
    # 深圳示例
    shenzhen_url = ('https://www.szcredit.org.cn/web/WebPages/Member'
                    '/CheckCode.aspx')
    r = requests.get(shenzhen_url, verify=False)
    img = Image.open(StringIO(r.content))
    r.close()
    ocr_str = image_recognition(img, 'shenzhen', show=True)
    print(ocr_str)
    # # 云南示例
    # yunnan_url = 'http://gsxt.ynaic.gov.cn/notice/captcha?preset=0'
    # r = requests.get(yunnan_url, verify=False)
    # img = Image.open(StringIO(r.content))
    # ocr_str = image_recognition(img, 'yunnan', True, '-psm 7 character')
    # print('yunnan check code is: {}'.format(ocr_str))
    # r.close()
    # # 上海示例
    # shanghai_url = 'https://www.sgs.gov.cn/notice/captcha?preset=0'
    # r = requests.get(shanghai_url, verify=False)
    # img = Image.open(StringIO(r.content))
    # ocr_str = image_recognition(img, 'shanghai', True, '-psm 10 character')
    # print('shanghai check code is: {}'.format(ocr_str))
    # r.close()
    # # 河北示例
    # hebei_url = 'http://www.hebscztxyxx.gov.cn/notice/captcha?preset=0'
    # r = requests.get(hebei_url, verify=False)
    # img = Image.open(StringIO(r.content))
    # ocr_str = image_recognition(img, 'hebei', True, '-psm 10 character')
    # print('hebei check code is: {}'.format(ocr_str))
    # r.close()