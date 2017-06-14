# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'yunnan'
from common import conf,common
import requests
from bs4 import BeautifulSoup
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
Session = requests.Session()
result = {}

def get_html(url, *para):
    headers_info = {
                'Connection': 'keep-alive',
                'Host' :'gsxt.hnaic.gov.cn',
                'Referer': 'http://gsxt.hnaic.gov.cn/notice/search/ent_info_list',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
                 }
    if para[0]!={}:
        data = para[0]
        req = Session.post(url, timeout=20, headers=headers_info, data=data)#, cookies = cookies)
    else:
        req = Session.post(url, timeout=20, headers=headers_info)#, cookies = cookies)
    content = req.text  # req.content.decode('utf-8')
    if len(content)<=150:# 这里可以再完善
        return None
    soup = BeautifulSoup(content, 'lxml')
    return soup

def detailPage(pageSoup, execute_d):
    # url_home
    detailTagValue = "mortageTable"
    mulpageTagValue = "spanmort"
    dlinkList = []
    pagelt = 2
    try:
        info = pageSoup.find(id=detailTagValue)  # 动产抵押登记信息的详情
        dlinkList = info.findAll('a')
    # 翻页tag
    #     for i in range(2, 100):
    #         page_i_tag = pageSoup.find(id=mulpageTagValue + str(i))
    #         if page_i_tag == None:
    #             pagelt = i  # max j is i-1.
    #             break
    #     if pagelt > 2:
    #         raise ValueError("pagelt > 2.")
    #         # for j in range(2, pagelt):
    #         #     url = url_home + "QueryMortList.jspx?"
    #         #     data = {'pno': str(j), 'mainId': id, 'ran':'0.5802342688028646'}
    #         #     pageSoup = get_html(url, data)
    #         #     print pageSoup
    #         #     info = pageSoup.find(id=detailTagValue)
    #         #     dlinkList = dlinkList + info.findAll('a')
    except:
        pass
    if dlinkList != []:
        pool_d = Pool_d()
        for c in execute_d:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            for d in dlinkList:
                dlink = d['href']
                print dlink
                pageSoup_d = get_html(dlink, {})
                if pageSoup_d != None:
                    result[conf.tableDict[c]] = getattr(pool_d, c)(dlink, pageSoup_d)
                    # common.for_print(result_D)

class Pool():

    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, pageSoup):
        br_keyword = [u"基本信息"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_="info m-bottom m-top")
        if dict_ba != {}:
            dict_ba = common.basicinfo_dict(dict_ba,u'云南')
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, pageSoup):
        br_keyword = ["exceptTable"]
        key_list = ['xuhao', 'reason','date_occurred','reason_out','date_out','authority']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, pageSoup):
        br_keyword = ["punishTable"]
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authirty', 'pun_date', 'gongshiriqi', 'xiangqing']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, pageSoup):
        br_keyword = ["alterTable"]
        key_list = ['reason', 'before_changes', 'after_changes', 'date_to_changes']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, pageSoup):
        br_keyword = ["branchTable"]
        key_list = ['xuhao','company_num','company_name','authority']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, pageSoup):
        br_keyword = ["memberTable"]
        key_list = ['xuhao','person_name','p_position']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, pageSoup):
        br_keyword = ["mortageTable"]
        key_list = ['xuhao','mortgage_reg_num','date_reg','authority','amount','status','gongshiriqi','xiangqing']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, pageSoup):
        br_keyword = ["pledgeTable"]
        key_list = ['xuhao','reg_code','pleder','id_card','plede_amount','brower','brower_id_card','reg_date','staues','gongshiriqi','changes']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, pageSoup):
        br_keyword = ["investorTable"]
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'xiangqing']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, pageSoup):
        number = 5
        br_keyword = ["spotcheckTable"]
        key_list = ['xuhao','authority','spot_type','spot_date','spot_result']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, pageSoup):
        info = pageSoup.find('div', rel = "layout-06_01")
        if info != None and info.findAll('div') != []:
            raise ValueError("This part's [info.findAll('div')] is not empty. You can check the div tag now.")
        else:
            return None

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, pageSoup):
        info = pageSoup.find('div', rel = "layout-06_01")
        if info != None and info.findAll('div') != []:
            raise ValueError("This part's [info.findAll('div')] is not empty. You can check the div tag now.")
        else:
            return None

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, pageSoup):
        key_list = ['xuhao','reason_in','date_in','reason_out','date_out','authority','xiangqing']
        br_keyword = ["blackTable"]
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, dlink, pageSoup):
        br_keyword = [u"动产抵押登记信息"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_="info m-bottom m-top")
        dict_ba = common.c_mortgage_dict(dict_ba)
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, dlink, pageSoup):
        br_keyword = [u"被担保债权概况"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_='info m-bottom m-top')
        dict_ba = common.s_creditor_dict(dict_ba)
        mortgage_reg_num = self.c_mortgage_execute(dlink, pageSoup)[0]['mortgage_reg_num']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, dlink, pageSoup):
        br_keyword = ["mortgageGuaTable"]
        key_list = ['xuhao','mortgage_name','belongs','information','mortgage_range']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(dlink, pageSoup)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

def main(b_list):
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时(or: 针对股权冻结和股权变更，div查询结果不为[]时)，raise error。
    # raise error的已经设置了先运行。
    executeA = [
        'black_info_execute', 'basicinfo_execute', 'adm_punishment_execute', 's_h_execute', 'b_c_execute',
        'branch_execute', 'member_execute', 'abnormal_execute', 'pledge_execute','spot_check_execute', 'mortgage_basic_execute'
    ]
    executeB = [
        'stock_freeze_execute', 'stockholder_change_execute'
    ]
    execute_d = ['c_mortgage_execute', 's_creditor_execute','mortgage_execute']
    pool = Pool()
    url_A = b_list.replace('\n','')
    url_B = url_A.split("tab=")[0]+"tab=06"

    # 司法协助公示信息
    pageSoup_B = get_html(url_B, {})
    if pageSoup_B != None:
        for c in executeB:
            # print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] =  getattr(pool, c)(pageSoup_B)
            # common.for_print(result_B)

    # 工商公示信息
    pageSoup_A = get_html(url_A, {})
    if pageSoup_A != None:
        for c in executeA:
            # print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] =  getattr(pool, c)(pageSoup_A)
            # common.for_print(result[conf.tableDict[c]])

    # 以下是获取详情html的
    detailPage(pageSoup_A, execute_d)
    return result


if __name__ == '__main__':
    L = [
        # 'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=3yi65vy6OWKpRQ5FDpBBmyfBa_aGXWpF&tab=01'
        # 'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=3yi65vy6OWKpRQ5FDpBBmyfBa_aGXWpF&tab=01'
        # 'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=Wh_Lkx.KcJZfRGUfw5O2_ClNEM3IUp7u&tab=01',#（变更信息）临湘市腾讯网络会所
        # 'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=Ssj9bXR3rXXkhjJ0BLuM_TRuaWxi469e&tab=01',#（股东，主要人员）湖南腾讯雷电子技术有限公司
        'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=am0Tuetld_1v3BqWegJRWmf_cOC.JWMR&tab=01',#（经营异常）湖南国腾讯达信息科技有限公司
        # 'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=OUYHjDJMDMMGNAk4newABLgsgFNsEpBl&tab=01',#（动产抵押，股权出质，抽查检查）桃源县竹园发电有限责任公司
        # 'http://gsxt.hnaic.gov.cn/notice/notice/view?uuid=K4mjYBV8qFcsqwXpEwyXmUhepf3uMKD0&tab=01',  #（分支机构【翻页】）岳阳华润燃气有限公司
    ]
    for b_list in L:
        main(b_list)

