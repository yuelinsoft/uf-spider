# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'jiangshu'
from common import conf,common
import requests
import re
import json
from bs4 import BeautifulSoup
import time
Session = requests.Session()
result = {}

'''
备忘:
number 的值其实并没有用到，先保留着。
get_html 可以获取翻页的内容
'''

def get_html(url1, list_, data_dict0):
    url0 = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/'
    url = url0 + url1
    headers_info = {
        'Connection': 'keep-alive',
        'Host': 'gsxt.lngs.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    }
    data = {'pripid': str(list_[0]),'type': str(list_[3])}
    for key in data_dict0:
        data[key] = data_dict0[key]
    req = Session.post(url, headers=headers_info, data=data)
    content = req.text
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_dict_2(pageSoup, *br_keyword):
    box = pageSoup.find(text=br_keyword[0]).find_parent('tr').next_siblings
    box = list(box)
    names_list = []
    data_list = []
    for i in range(len(box)):
        if len(str(box[i])) > 3:
            names_list = names_list + map(lambda n: n, map(
                lambda n: n.get_text().strip().replace('\r\n', '').replace('\t', '').replace(' ', ''),
                (box[i].find_all('th'))))
            data_list = data_list + map(lambda m: m, map(
                lambda n: n.get_text().strip().replace('\r\n', '').replace('\t', '').replace(' ', ''),
                (box[i].find_all('td'))))
    dict_ba = dict(zip(names_list, data_list))
    return dict_ba

def get_dict_list_3(pageSoup, *br_keyword):
    dict_ba_list = []
    p = br_keyword[0]
    b = re.search(p,str(pageSoup))
    if b != None:
        s = b.group()
        if len(s)>120:
            # 只有[1]这个地方跟common.get_dict_list_2不一样，后续尽量把它合并进来。
            s = s.split("]",-1)[1]+"]"
            if len(s.split("["))>1:
                s = "["+s.split("[")[1]
                jsonA = json.loads(s)
    return jsonA

def detailPage(list_, execute_d):
    url0 = 'http://gsxt.lngs.gov.cn/saicpub/entPublicitySC/entPublicityDC/'
    url1 = 'getDcdydjAction.action'
    url = url0 + url1
    number = 8
    br_keyword = "script"
    pageSoup = get_html(url1, list_, [])
    aList = []
    p = r"document[\s\S]*\/script"
    b = re.search(p,str(pageSoup))
    if b == None:
        pass
    else:
        s = b.group()
        if len(s)>120:
            s = s.split("]",-1)[0]+"]"
            if len(s.split("["))>1:
                s = "["+s.split("[")[1]
                jsonA = json.loads(s)
                for a in jsonA:
                    aList.append(a["dcdydjid"])
    if aList != []:
        url1 = 'getDcdyDetailAction.action'
        for a in aList:
            data_dict0 = {"dcdydjid":a}
            pageSoup_d = get_html(url1, list_, data_dict0)
            b = common.get_b(pageSoup_d)
            pool_d = Pool_d()
            for c in execute_d:
                result[conf.tableDict[c]] = getattr(pool_d, c)(pageSoup_d,b)
                # common.for_print(result_D)

class Pool():
    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, list_):
        url1 = 'getJbxxAction.action'
        br_keyword = "jibenxinxi"
        pageSoup = get_html(url1, list_, [])
        dict_ba = common.get_dict(pageSoup, br_keyword)
        for d in dict_ba: print d,dict_ba[d]
        if dict_ba != {}:
            dict_ba = common.basicinfo_dict(dict_ba,u'辽宁')
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, list_):
        url1 = 'getJyycxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao', 'reason','date_occurred','reason_out','date_out','authority']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚###
    def adm_punishment_execute(self, list_):
        url1 = 'getXzcfxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authirty', 'pun_date', 'gongshiriqi', 'xiangqing']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, list_):
        url1 = 'getBgxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['reason', 'before_changes', 'after_changes', 'date_to_changes']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, list_):
        url1 = 'getFgsxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','company_num','company_name','authority']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要成员信息）
    def member_execute(self, list_):
        url1 = 'getZyryxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','person_name','p_position']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, list_):
        url1 = 'getDcdydjAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','mortgage_reg_num','date_reg','authority','amount','status','gongshiriqi','xiangqing']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息###
    def pledge_execute(self, list_):
        url1 = 'getGsgsGqczxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','reg_code','pleder','id_card','plede_amount','brower','brower_id_card','reg_date','staues','gongshiriqi','changes']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, list_):
        url1 = 'getTzrxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'xiangqing']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, list_):
        url1 = 'getCcjcxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','authority','spot_type','spot_date','spot_result']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息
    def stock_freeze_execute(self, list_):
        url1 = 'getSfgsGqdjxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','person','stock','court','notice_number','statues','xiangqing']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_STOCKHOLDER_CHANGE股权更变信息
    def stockholder_change_execute(self, list_):
        url1 = 'getSfgsGdbgxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','person','stock','person_get','court','xiangqing']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, list_):
        url1 = 'getYzwfxxAction.action'
        br_keyword = r"document[\s\S]*\/script"
        pageSoup = get_html(url1, list_, [])
        key_list = ['xuhao','reason_in','date_in','reason_out','date_out','authority','xiangqing']
        dict_ba_list = common.get_dict_list_2(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）#
    def c_mortgage_execute(self, pageSoup):
        br_keyword = u"动产抵押登记信息"
        dict_ba = get_dict_2(pageSoup, br_keyword)
        dict_ba = common.c_mortgage_dict(dict_ba)
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list


    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）#
    def s_creditor_execute(self, pageSoup):
        br_keyword = u"被担保债权概况"
        dict_ba = get_dict_2(pageSoup, br_keyword)
        dict_ba = common.s_creditor_dict(dict_ba)
        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0]['mortgage_reg_num']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list


    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）##
    def mortgage_execute(self, pageSoup):
        key_list = ['xuhao','mortgage_name','belongs','information','mortgage_range']
        br_keyword = r"document[\s\S]*\/script"
        dict_ba_list = get_dict_list_3(pageSoup, br_keyword)
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

def main(tag_list):
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时，raise error。
    executeA = ['stock_freeze_execute','stockholder_change_execute','black_info_execute',
                'basicinfo_execute','b_c_execute','s_h_execute','member_execute','abnormal_execute',
                'adm_punishment_execute','branch_execute','mortgage_basic_execute',
                'pledge_execute','spot_check_execute'
              ]
    execute_d = ['c_mortgage_execute','s_creditor_execute','mortgage_execute']
    pool = Pool()
    for c in executeA:
        print "%r %r %r"%("*"*20, c, "*"*20)
        result[conf.tableDict[c]] =  getattr(pool, c)(tag_list)
        # common.for_print(result_A)

    # 以下是获取详情html的
    detailPage(tag_list, execute_d)
    return result


if __name__ == '__main__':
    Tlist = [
    # [u'21030400002201402244984X', u'\u978d\u5c71\u817e\u8baf\u4f20\u5a92\u6709\u9650\u516c\u53f8', u'210300005194668',u'1151', u'1'],#鞍山腾讯传媒有限公司(变更信息，主要成员，股东)
    # [u'210202000022014103000821',u'\u5927\u8fde\u878d\u91d1\u6240\u6295\u8d44\u54a8\u8be2\u6709\u9650\u516c\u53f8', u'210202000061113',u'1151', u'1'], # 大连融金所投资咨询有限公司 （经营异常信息）
    # [u'210200000022004083000010', u'\u5927\u8fde\u4e7e\u701a\u56fd\u9645\u7269\u6d41\u6709\u9650\u516c\u53f8',u'91210200764420750T', u'1130', u'1'],  # 大连乾瀚国际物流有限公司(股权出质，动产抵押)
    # [u'210202000022005041900327', u'\u5927\u8fde\u601d\u5ba2\u901a\u8baf\u670d\u52a1\u4e2d\u5fc3',u'210202000014844', u'4540', u'1'],  # 大连思客通讯服务中心(抽查检查信息)
    # [u'210200000011949090100013', u'\u5927\u8fde\u71c3\u6c14\u96c6\u56e2\u6709\u9650\u516c\u53f8',u'210200000263588', u'1190', u'1'],  # 大连燃气集团有限公司(分支机构)
    # [u'210202000012008010800076', u'\u5927\u8fde\u65b0\u5546\u62a5\u793e', u'210202000014869', u'3100', u'1'],# 大连新商报社(行政处罚)
    ]

    for tag_list in Tlist:
        print tag_list[2]
        main(tag_list)
        print "*******"
        time.sleep(5)
