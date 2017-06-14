#-*- coding:utf-8 -*-
from __future__ import unicode_literals
import os,os.path
import sys
# csv文件和jpg文件的路径
# proxy ip

confPath = os.path.dirname(__file__)
# CommonDir = os.path.join(confPath, "common",)
dictoryPath = os.path.join(confPath, "dictory.txt")#成语库
ImgBaseDir = os.path.join(os.path.dirname(confPath), "cache_img",)
csvDir = os.path.join(os.path.dirname(confPath), "train_operator",)
# 格式：ImgDir = os.path.join(ImgBaseDir,"c7_shandong_img",)
# 格式：csvPath = os.path.join(csvDir,"c7_shandong_train_opeator.csv")

tableDict = {
    'basicinfo_execute': 'qyxx_basicinfo',
    's_h_execute': 'qyxx_s_h',
    'b_c_execute': 'qyxx_b_c',
    'member_execute': 'qyxx_member',
    'branch_execute': 'qyxx_branch',
    'mortgage_basic_execute': 'qyxx_mortgage_basic',
    'pledge_execute': 'qyxx_pledge',
    'adm_punishment_execute': 'qyxx_adm_punishment',
    'abnormal_execute': 'qyxx_abnormal',
    'black_info_execute': 'qyxx_black_info',
    'spot_check_execute': 'qyxx_spot_check',
    'c_mortgage_execute': 'qyxx_c_mortgage',
    's_creditor_execute': 'qyxx_s_creditor',
    'mortgage_execute': 'qyxx_mortgage',
    'stock_freeze_execute': 'qyxx_stock_freeze',
    'stockholder_change_execute': 'qyxx_stockholder_change'
    }

# provDict中没有写了爬虫脚本的省份先注释。
provDict = {
    '广州': 'd1_guangdong',
    '深圳': 'h2_shenzhen',
    # '北京': 'a1_beijing',
    # '天津': 'a2_tianjin',
    '河北': 'a3_hebei',
    # '山西': 'a4_shanxi',
    # '内蒙古': 'a5_neimenggu',
    # '辽宁': 'b1_liaoning',
    # '吉林': 'b2_jilin',
    # '黑龙江': 'b3_heilongjiang',
    '上海': 'c1_shanghai',
    '江苏': 'c2_jiangsu',
    # '浙江': 'c3_zhejiang',
    # '安徽': 'c4_anhui',
    # '福建': 'c5_fujian',
    # '江西': 'c6_jiangxi',
    # '山东': 'c7_shandong',
    '广东': 'd1_guangdong',
    '广西': 'd2_guangxi',
    # '海南': 'd3_hainan',
    # '河南': 'e1_henan',
    # '湖北': 'e2_hubei',
    # '湖南': 'e3_hunan',
    '重庆': 'f1_chongqing',
    # '四川': 'f2_sichuan',
    '贵州': 'f3_guizhou',
    '云南': 'f4_yunnan',
    # '西藏': 'f5_xizang',
    # '陕西': 'g1_shaanxi',
    # '甘肃': 'g2_gansu',
    # '青海': 'g3_qinghai',
    # '宁夏': 'g4_ningxia',
    # '新疆': 'g5_xinjiang',

}

