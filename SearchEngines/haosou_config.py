#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

"""
    haosou_config
    ~~~~~~~~~

    好搜爬虫与字典分发配置

    :copyright: (c) 2017 by cds@uf-club.
    :license: MIT, see LICENSE for more details.
"""

__versions__ = '5.0.1'

# haosou_pre_processing.py 参数配置
QUERY_KEY = ['name', 'id_num', 'phone1', 'phone2', 'phone3', 'company',
             'company_phone1', 'company_phone2', 'company_phone3',
             'spouse_name', 'spouse_id_card', 'spouse_phone1', 'spouse_phone2',
             'contact_phone1', 'contact_phone2', 'contact_phone3',
             'contact_phone4', 'contact_phone5', 'contact_phone6',
             'contact_phone7', 'contact_phone8']
COMPOSITE_KEY_DICT = {'company_phone1_special': ['company_phone1'],
                      'company_phone2_special': ['company_phone2'],
                      'company_phone3_special': ['company_phone3'],
                      # 'company_search': ['company', ['电话']],
                      }
PAGE_DICT = {'name': 5,
             'id_num': 5,
             'phone1': 5,
             'phone2': 5,
             'phone3': 5,
             # 'company': 5,
             'company': 1,
             'company_phone1': 5,
             'company_phone2': 5,
             'company_phone3': 5,
             'spouse_name': 5,
             'spouse_id_card': 5,
             'spouse_phone1': 5,
             'spouse_phone2': 5,
             'contact_phone1': 5,
             'contact_phone2': 5,
             'contact_phone3': 5,
             'contact_phone4': 5,
             'contact_phone5': 5,
             'contact_phone6': 5,
             'contact_phone7': 5,
             'contact_phone8': 5,
             'company_phone1_special': 1,
             'company_phone2_special': 1,
             'company_phone3_special': 1,
             # 'company_search': 1,
             }
# haosou_crawler.py 参数配置
ID_CARD_MAP_KEY = ['id_num', 'spouse_id_card']
PHONE_MAP_KEY = ['phone1', 'phone2', 'phone3', 'company_phone1',
                 'company_phone2', 'company_phone3', 'spouse_phone1',
                 'spouse_phone2', 'contact_phone1', 'contact_phone2',
                 'contact_phone3', 'contact_phone4', 'contact_phone5',
                 'contact_phone6', 'contact_phone7', 'contact_phone8']
COMPANY_PHONE_KEY = ['company_phone1', 'company_phone2', 'company_phone3']
CHECK_TIME_MAP = {'name': '',
                  'id_num': '',
                  'phone1': '',
                  'phone2': '',
                  'phone3': '',
                  'company': '',
                  'company_phone1': '',
                  'company_phone2': '',
                  'company_phone3': '',
                  'spouse_name': '',
                  'spouse_id_card': '',
                  'spouse_phone1': '',
                  'spouse_phone2': '',
                  'contact_phone1': '',
                  'contact_phone2': '',
                  'contact_phone3': '',
                  'contact_phone4': '',
                  'contact_phone5': '',
                  'contact_phone6': '',
                  'contact_phone7': '',
                  'contact_phone8': '',
                  'company_phone1_special': 'y',
                  'company_phone2_special': 'y',
                  'company_phone3_special': 'y',
                  # 'company_search': 'y',
                  }
SO_HEADERS = {'Host': 'www.so.com',
              'Referer': 'https://www.so.com/',
              'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit'
                            '/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 '
                            'Safari/537.36}',
              'Connection': 'keep-alive',
              'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,'
                        'image/webp,*/*;q=0.8',
              }
HAOSO_BASIC_URL = 'https://www.so.com/s?q={query_term}&j=1&pn={page}'
HAOSO_URL_WITH_TIME = ('https://www.so.com/s?q={query_term}&j=1&pn={'
                       'page}&adv_t={time}')
A_LEVEL_BLACK_LIST = ['贷款', '纠纷', '刑', '欠债', '欠款', '欠条', '欠税', '欠费',
                      '欠钱', '欠薪', '借债', '还债', '外债', '债主', '债权', '负债',
                      '讨债', '逃债', '债务', '债款', '赌博', '赌徒', '赌债', '赌注',
                      '毒瘾', '拖欠', '冻结', '冰毒', '摇头丸', '毒品', '博彩',
                      '六合彩', '跑路', '黑名单', '逾期', '不良', '破产', '倒闭',
                      '老赖', '无赖', '催收', '失信', '欠钱', '借钱', '赌钱', '洗钱',
                      '钱庄', '坑钱', '坑人', '坑骗', '骗子', '骗钱', '骗贷', '虚假',
                      '诉讼', '借钱', '借贷', '借据', '信贷', '网贷', '抵押', '质押',
                      '担保', '信用', '小贷', 'P2P', 'POS', '互联网金融', '金朝阳',
                      '创富港', '非法', '查封', '转让', '房屋出售', '欠租', '诈骗',
                      '毒品', '出租', '集资', '融资', '抵押担保', '融资担保',
                      '非法融资', '非法集资', '还钱']
B_LEVEL_BLACK_LIST = ['赌场', '处罚', '坑害', '拐卖', '造假', '作假', '做假', '逃债',
                      '逃跑', '盗窃', '偷盗', '欺负', '欺骗', '谋害', '杀害', '害人',
                      '黑榜', '被执行人', '违法', '违章', '违纪', '违规', '违反',
                      '酒吧', '按摩', '桑拿', '洗浴', '足浴', '夜总会', '军人',
                      '律师', '基金', '期货投资', '信息咨询', '家具', '大宗商品',
                      '钢铁', '钢贸', 'PE', 'VC', '信托', '理财', '资本', '财商',
                      '中介', '包装', '投资', '重组', '争议', '谎言', '困境', '自首',
                      '被逼', '不合格', '曝光', '整改', '举报', '司法', '审判',
                      '立案', '不法', '涉法', '案例', '问题', '案件', '起诉', '原告',
                      '被告', '上诉', '被查', '改正', '停业', '亏损', '报仇', '裁判',
                      '裁决', '裁定', '收购', '污点', '事故', '严惩', '受贿', '贪污',
                      '行贿', '责令', '假冒', '侵权', '欠费', '欠税', '侵害',
                      '不正当', '涉嫌', '逮捕', '作案', '受害人', '拍卖', '涉黑',
                      '黑心', '罚款', '侵犯', '拘留', '骚扰', '殴打', '审理',
                      '股权投资', '贵金属投资']
C_LEVEL_BLACK_LIST = ['法院']
SPECIAL_BLACK_LIST = ['病']
BLACK_LIST_MAP = {'name': A_LEVEL_BLACK_LIST,
                  'id_num': A_LEVEL_BLACK_LIST + SPECIAL_BLACK_LIST,
                  'phone1': A_LEVEL_BLACK_LIST + SPECIAL_BLACK_LIST,
                  'phone2': A_LEVEL_BLACK_LIST + SPECIAL_BLACK_LIST,
                  'phone3': A_LEVEL_BLACK_LIST + SPECIAL_BLACK_LIST,
                  'company': A_LEVEL_BLACK_LIST + B_LEVEL_BLACK_LIST +
                             C_LEVEL_BLACK_LIST,
                  'company_phone1': A_LEVEL_BLACK_LIST,
                  'company_phone2': A_LEVEL_BLACK_LIST,
                  'company_phone3': A_LEVEL_BLACK_LIST,
                  'spouse_name': A_LEVEL_BLACK_LIST,
                  'spouse_id_card': A_LEVEL_BLACK_LIST,
                  'spouse_phone1': A_LEVEL_BLACK_LIST,
                  'spouse_phone2': A_LEVEL_BLACK_LIST,
                  'contact_phone1': A_LEVEL_BLACK_LIST,
                  'contact_phone2': A_LEVEL_BLACK_LIST,
                  'contact_phone3': A_LEVEL_BLACK_LIST,
                  'contact_phone4': A_LEVEL_BLACK_LIST,
                  'contact_phone5': A_LEVEL_BLACK_LIST,
                  'contact_phone6': A_LEVEL_BLACK_LIST,
                  'contact_phone7': A_LEVEL_BLACK_LIST,
                  'contact_phone8': A_LEVEL_BLACK_LIST,
                  'company_phone1_special': [],
                  'company_phone2_special': [],
                  'company_phone3_special': [],
                  # 'company_search': [],
                  }
# 网站来源过滤
SOURCE_SAVE_LIST = ['风险信息网', '全国法院被执行信息查询网', '中国裁判文书网',
                    '汇法网', '中国执行信息公开网', '360手机应用']
SOURCE_FILTER_LIST = ['优酷', '我乐网', '三藏算命', '当当网', '果壳网', '爱问问网',
                      '17K小说网', '8252小游戏', '请看小说网', '腾讯微博', '土豆网',
                      '搜狐视频', '凤凰视频', '乐视视频']
# 规则化
FORMAT_IMG_SCR = '<img src="data{}">'
FORMAT_OR_REGEX = '(?:{})'
FORMAT_OFFICIAL_TITLE = '【官网】{}'
FORMAT_POST_TIME = '{0}-{1}-{2}'
FORMAT_BLACK_LIST_TAG = '<strong>{}</strong>'
FORMAT_REDIRECT_SCRIPT = """<meta content="always" name="referrer">
<script>window.location.replace("{0}")</script>
<noscript>
<meta http-equiv="refresh" content="0;URL='{1}'">
</noscript>
"""
# 地图 在线观看 视频等不查询
SUMMARY_SWITCH_DICT = {'最新相关消息': '<p class="mh-first-cont">(.*?)...</p>',
                       '博客': '<a.*?-type="link".*?>(.*?)</a',
                       '微博': 'wb-text">(?:.*?</span>|.*?)(.*?)<a',
                       '问答': '最佳答案：</span>(.*?)<a',
                       '在线观看': '<p class="video-ext">.*?</p>(.*?)<p',
                       }
# 使用到的正则表达式
REGEX_PAGE_EXCEPTION = '访问异常出错'
REGEX_PAGE_ITEM = 'lass="res-list".*?>([\s\S]*?)</li>(?:<li c|</ul>)'
REGEX_IMG_SCR = '<img src="data(.*?)"'
REGEX_TITLE = '<a.*?(?:data-res|data-md=\'{"(?:b|p)":"title"}\').*?>(.*?)</a>'
REGEX_OFFICIAL = 'icon-official">官网</span>'
REGEX_SUMMARY = '(?:<p.*?class="res-desc".*?|<div class.*?><p)>(.*?)<(?:/p|a)'
REGEX_SUMMARY_OTHER = '<div class="res-comm-con"(?:| )>(?:.*?</span>|)(.*?)<p'
REGEX_SUMMARY_TYPE = '(?:最新相关消息|博客|微博|问答|在线观看)'
REGEX_CACHED_URL = '</cite>-<a href="(.*?)" target="_blank" class="m">快照</a>'
REGEX_HOME_URL = '<a href="(.*?)" rel="noopener"'
REGEX_SOURCE = 'class="mingpian".*?>(?:<span class="tip-v"></span>|)(.*?)</a>'
REGEX_POST_TIME = '(201\d)(?:年|-)(\d{1,2})(?:月|-)(\d{1,2})(?:日|)'
REGEX_DIRECT_URL = 'replace\("(.*?)"\)'