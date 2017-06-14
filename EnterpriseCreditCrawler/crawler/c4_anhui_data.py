# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'anhui'
from common import conf,common
import requests
from bs4 import BeautifulSoup
import re
Session = requests.Session()
result = {}

def get_html(url, *para):
    headers_info = {
        'Connection': 'keep-alive',
        'Host': 'www.ahcredit.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36',
    }
    if para[0]!={}:
        data = para[0]
        req = Session.post(url, timeout=20, headers=headers_info, data=data)
    else:
        req = Session.post(url, timeout=20, headers=headers_info)
    content = req.text
    # print content
    if len(content)<=150:# 这里可以再完善
        return None
    soup = BeautifulSoup(content, 'lxml')
    return soup

def mul_page(pageSoup, page_tag, url_page_part, key_list, dlink, idname, glb_id):
    # 这个只能判断初始的pageSoup中带的翻页tag，如果页数太多的话是不ok的，因为改变后的pageSoup不会找得到的。
    '''
    id, idname: 针对动产抵押详情页面的翻页情况，key并不等于'mainId'，需要idname传值，key对应的value用id存；
    pagelt: page limit, 页数限制边缘值，用于range中，比最大页数大1，初始值为2；
    i：结合page_tag，查找是否存在翻页的情况，并将找到的最大值赋值给pagelt，因此从2开始循环查找；
    j： 获取翻页html时传data需要用到.
    '''
    dict_ba_list = []
    id = glb_id
    url_home = "http://www.ahcredit.gov.cn/"
    id = id.split("=")[-1]
    pagelt = 2
    for i in range(2, 100):
        page_i_tag = pageSoup.find(id=page_tag + str(i))
        if page_i_tag == None:
            pagelt = i  # max j is i-1.
            break
    for j in range(1, pagelt):
        url = url_home + url_page_part
        if idname != "":# 针对抵押物的翻页
            if dlink != "":
                a = re.findall("[0-9]+", dlink)
                if a != []:
                    id = a[0]
            data = {'pno': str(j), idname: id}
        else:
            data = {'pno': str(j), 'mainId': id}
        pageSoup = get_html(url, data)
        if pageSoup != None:
            br_keyword = [""]
            dict_ba_list_0 = common.get_dict_list(pageSoup, key_list, br_keyword)
            dict_ba_list=dict_ba_list+dict_ba_list_0
    return dict_ba_list

def detailPage(pageSoup_A, execute_d, glb_id):
    url_home = "http://www.ahcredit.gov.cn/"
    detailTagValue = "mortDiv"
    mulpageTagValue = "spanmort"
    dlinkList = []
    pagelt = 2
    try:
        # info = pageSoup_A.find(id = "mortDiv")#动产抵押登记信息的详情
        info = pageSoup_A.find('div', id=detailTagValue)
        dlinkList = info.findAll('a')
        for i in range(2, 100):
            page_i_tag = pageSoup_A.find(id=mulpageTagValue + str(i))
            if page_i_tag == None:
                pagelt = i  # max j is i-1.
                break
        if pagelt > 2:
            raise ValueError("pagelt > 2.")
            # for j in range(2, pagelt):
            #     url = url_home + "QueryMortList.jspx?"
            #     data = {'pno': str(j), 'mainId': id, 'ran':'0.5802342688028646'}
            #     pageSoup = get_html(url, data)
            #     print pageSoup
            #     info = pageSoup.find(id=detailTagValue)
            #     dlinkList = dlinkList + info.findAll('a')
    except:
        pass
    if dlinkList != []:
        pool_d = Pool_d(glb_id)
        for c in execute_d:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            for d in dlinkList:
                dlink = d['onclick']
                url = url_home + dlink.split("'")[1]
                print url
                pageSoup_d = get_html(url, {})
                if pageSoup_d != None:
                    result[conf.tableDict[c]] = getattr(pool_d, c)(dlink, pageSoup_d)
                    # common.for_print(result_D)

class Pool():

    def __init__(self, glb_id):
        self.glb_id = glb_id

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, pageSoup):
        br_keyword = [u"基本信息"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_="detailsList")
        if dict_ba != {}:
            dict_ba = common.basicinfo_dict(dict_ba,u'安徽')
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, pageSoup):
        # br_keyword = ["excDiv"]
        page_tag = "spanexc"
        url_page_part = "QueryExcList.jspx?"
        key_list = ['xuhao', 'reason','date_occurred','reason_out','date_out','authority']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, pageSoup):
        # br_keyword = ["punDiv"]
        page_tag = "spanpun"
        url_page_part = "QueryPunList.jspx?"
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authirty', 'pun_date', 'gongshiriqi', 'xiangqing']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, pageSoup):
        # br_keyword = ["altDiv"]
        page_tag = "spanalt"
        url_page_part = "QueryAltList.jspx?"
        key_list = ['reason', 'before_changes', 'after_changes', 'date_to_changes']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, pageSoup):
        # br_keyword = ["childDiv"]
        page_tag = "spanchild"
        url_page_part = "QueryChildList.jspx?"
        key_list = ['xuhao','company_num','company_name','authority']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, pageSoup):
        # br_keyword = ["memDiv"]
        page_tag = "spanmem"
        url_page_part = "QueryMemList.jspx?"
        key_list = ['xuhao','person_name','p_position']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, pageSoup):
        # br_keyword = ["dongchandiya"]
        page_tag = "spanmort"
        url_page_part = "QueryMortList.jspx?"
        key_list = ['xuhao','mortgage_reg_num','date_reg','authority','amount','status','gongshiriqi','xiangqing']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, pageSoup):
        # br_keyword = ["guquanchuzhi"]
        page_tag = "spanpledge"
        url_page_part = "QueryPledgeList.jspx?"
        key_list = ['xuhao','reg_code','pleder','id_card','plede_amount','brower','brower_id_card','reg_date','staues','gongshiriqi','changes']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, pageSoup):
        # br_keyword = [u"invDiv"]
        page_tag = "spaninv"
        url_page_part = "QueryInvList.jspx?"
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'xiangqing']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  "", "", self.glb_id)
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, pageSoup):
        br_keyword = ["chouchaxinxi"]
        key_list = ['xuhao','authority','spot_type','spot_date','spot_result']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息
    def stock_freeze_execute(self, pageSoup):
        br_keyword = ["EquityFreezeDiv"]
        key_list = ['xuhao','person','stock','court','notice_number','statues','xiangqing']
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, pageSoup):
        key_list = ['xuhao','person','stock','person_get','court','xiangqing']
        br_keyword = ["xzcfDiv"]
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, pageSoup):
        key_list = ['xuhao','reason_in','date_in','reason_out','date_out','authority','xiangqing']
        br_keyword = ["yanzhongweifaqiye"]
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

class Pool_d():

    def __init__(self, glb_id):
        self.glb_id = glb_id

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, dlink, pageSoup):
        br_keyword = [u"动产抵押登记信息"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_="detailsList")
        dict_ba = common.c_mortgage_dict(dict_ba)
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, dlink, pageSoup):
        br_keyword = [u"被担保债权概况"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_='detailsList')
        dict_ba = common.s_creditor_dict(dict_ba)
        mortgage_reg_num = self.c_mortgage_execute(dlink, pageSoup)[0]['mortgage_reg_num']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, dlink, pageSoup):
        # br_keyword = ["guaTab"]
        page_tag = "spangua"
        url_page_part = "QueryGuaList.jspx?"
        idname = "mortId"
        key_list = ['xuhao','mortgage_name','belongs','information','mortgage_range']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list,  dlink, idname, self.glb_id)
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(dlink, pageSoup)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

def main(id_number):
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时，raise error。
    id = id_number[-32:]
    glb_id = id
    url_home = "http://www.ahcredit.gov.cn/"
    url_part_A = "businessPublicity.jspx?id="
    url = url_home + url_part_A + id
    executeA = [#'black_info_execute','basicinfo_execute', 'abnormal_execute', 'adm_punishment_execute',
        'b_c_execute',
        # 'branch_execute', 'member_execute', 'mortgage_basic_execute', 'pledge_execute',
        # 's_h_execute', 'spot_check_execute'
    ]
    executeB = [
        'stockholder_change_execute', 'stock_freeze_execute'
    ]
    execute_d = ['c_mortgage_execute', 's_creditor_execute','mortgage_execute']
    pool = Pool(glb_id)

    # 工商公示信息
    # pageSoup_A = get_html(url, {})
    path = 'F:\\code\\1\\anhui\\pageA.html'
    with open(path, 'rb') as f:
        html = f.read()
    pageSoup_A = BeautifulSoup(html, 'lxml')
    if pageSoup_A != None:
        for c in executeA:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] =  getattr(pool, c)(pageSoup_A)
            # common.for_print(result_A)
    #
    # # 司法协助公示信息
    # url_B = url_home + "justiceAssistance.jspx?id=" + id
    # # pageSoup_B = get_html(url_B, {})
    # path = 'F:\\code\\1\\anhui\\pageB.html'
    # with open(path, 'rb') as f:
    #     html = f.read()
    # pageSoup_B = BeautifulSoup(html, 'lxml')
    # if pageSoup_B != None:
    #     for c in executeB:
    #         print "%r %r %r" % ("*" * 20, c, "*" * 20)
    #         result[conf.tableDict[c]] =  getattr(pool, c)(pageSoup_B)
    #         common.for_print(result_B)
    #
    # # 以下是获取详情html的
    # detailPage(pageSoup_A, execute_d, glb_id)
    #

if __name__ == '__main__':
    tag_list = [
            '/businessPublicity.jspx?id=DC436F2D5F2952118CDEB15D7F0EE103',  # 科大讯飞股份有限公司（股东信息，变更信息【翻页】，主要人员信息【翻页，双栏】，分支机构信息【翻页】）
            # '/businessPublicity.jspx?id=94EC2DC6E1F53A7E1D12A0844F0A8380',  # 安徽元枫管道科技股份有限公司(动产抵押登记信息)
            # '/businessPublicity.jspx?id=3B2B1D4C2DD9867D839C7C2D3747740E',  # 芜湖市五显正鸿新型建材有限公司(抵押物)
            # '/businessPublicity.jspx?id=D34A33EEB4FDFF677CA8B745E12C7F11',  # 安徽芜鑫商贸有限公司(经营异常信息)
            # '/businessPublicity.jspx?id=C9D6FA3CF97EFC05F2B5DB23DAD6CEA7',  # 芜湖江业超市(行政处罚)
            # '/businessPublicity.jspx?id=B95CA6533683CD5F43F17AA6EB289D85', # 安徽金沃农业有限公司（司法股权冻结信息）
            # '/businessPublicity.jspx?id=B95CA6533683CD5F43F17AA6EB289D85', # 芜湖禾田汽车工业有限公司(股权出质登记信息,动产抵押登记信息)
                ]
    for id_number in tag_list:
        main(id_number)
