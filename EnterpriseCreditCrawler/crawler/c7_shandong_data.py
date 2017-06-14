# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'shanghai', 'anhui'
from common import conf,common
import requests
from bs4 import BeautifulSoup
import re
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
Session = requests.Session()
result = {}

def get_html(url, *para):
    headers_info = {
        'Connection': 'keep-alive',
        'Host' :'218.57.139.24',
        'Accept-Encoding':'gzip, deflate, sdch',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36',
            }
    if para[0]!={}:
        data = para[0]
        req = Session.get(url, timeout=40, headers=headers_info, data=data)
    else:
        req = Session.get(url, timeout=40, headers=headers_info)
    content = req.text
    if len(content)<=150:# 这里可以再完善
        return None
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_html_2(url1, list_, pageSoup, data_dict0):
    token = ""
    dict_ba_list = []
    url0 = 'http://218.57.139.24'
    if url1 == "/pub/ccjcxx/" or url1 == '/pub/gsgqcz/':
        url = url0 + url1
    else:
        url = url0 + url1 + list_["enttype"]
    p = '''content="(.*?)"'''
    b = re.search(p,str(pageSoup.findAll('meta')[3]))
    if b != None:
        s = b.group()
        token = s.split('"')[1]
    headers_info = {
        'Connection': 'keep-alive',
        'Host' :'218.57.139.24',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'X-CSRF-TOKEN':token,
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'
    }
    data = {'encrpripid': str(list_['encrptpripid'])}
    for key in data_dict0:
        data[key] = data_dict0[key]
    req = Session.post(url, timeout=40, headers=headers_info, data=data)
    content = req.text
    dict_ba_list = json.loads(content)
    return dict_ba_list

def detailPage(pageSoup, list_, execute_d):
    url1 = '/pub/gsdcdy/'
    dict_ba_list = get_html_2(url1, list_, pageSoup, [])
    if dict_ba_list != []:
        raise ValueError("dict_ba_list is not empty.")
    # # url_home
    # detailTagValue = "mortageTable"
    # mulpageTagValue = "spanmort"
    # dlinkList = []
    # try:
    #     info = pageSoup.find(id=detailTagValue)  # 动产抵押登记信息的详情
    #     dlinkList = info.findAll('a')

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

    # except:
    #     pass
    # if dlinkList != []:
    #     pool_d = Pool_d()
    #     for c in execute_d:
    #         print "%r %r %r" % ("*" * 20, c, "*" * 20)
    #         for d in dlinkList:
    #             dlink = d['href']
    #             print dlink
    #             pageSoup_d = get_html(dlink, {})
    #             if pageSoup_d != None:
    #                 getattr(pool_d, c)(dlink, pageSoup_d)

class Pool():

    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, list_, pageSoup):
        br_keyword = [u"基本信息"]
        dict_ba = common.get_dict(pageSoup, br_keyword, class_="detailsList")
        if dict_ba != {}:
            dict_ba = common.basicinfo_dict(dict_ba,u'山东')
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, list_, pageSoup):
        url1 = '/pub/jyyc/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, list_, pageSoup):
        url1 = '/pub/gsxzcfxx/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, list_, pageSoup):
        br_keyword = "bgsxliststr"+r"[\s\S]*}]';"
        dict_ba_list = common.get_dict_list_2(pageSoup, *br_keyword)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, list_, pageSoup):
        url1 = '/pub/gsfzjg/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, list_, pageSoup):
        url1 = '/pub/gsryxx/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, list_, pageSoup):
        url1 = '/pub/gsdcdy/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, list_, pageSoup):
        url1 = '/pub/gsgqcz/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, list_, pageSoup):
        br_keyword = "czxxliststr"+r"[\s\S]*}]';"
        dict_ba_list = common.get_dict_list_2(pageSoup, *br_keyword)
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, list_, pageSoup):
        url1 = '/pub/ccjcxx/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, list_, pageSoup):
        br_keyword = "gqxxliststr"+r"[\s\S]*}]';"
        dict_ba_list = common.get_dict_list_2(pageSoup, *br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, list_, pageSoup):
        p = r'''script type="text/javascript">\s{1,10}var.{8,20}\[[\s\S]*}]';'''
        b = re.search(p, str(pageSoup))
        if b != None:
            s = b.group()
            if len(s)>20:
                raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, list_, pageSoup):
        url1 = '/pub/yzwfqy/'
        dict_ba_list = get_html_2(url1, list_, pageSoup, [])
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
        br_keyword = "mortgageGuaTable"+r"[\s\S]*}]';"
        dict_ba_list = common.get_dict_list_2(pageSoup, *br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
            # for dict_ba in dict_ba_list:
            #     mortgage_reg_num = self.c_mortgage_execute(dlink, pageSoup)[0]['mortgage_reg_num']
            #     dict_ba['mortgage_reg_num'] = mortgage_reg_num
        else:
            return None

def main(id_list):
    executeA = [
            'mortgage_basic_execute','adm_punishment_execute','black_info_execute',
            'basicinfo_execute', 'b_c_execute', 's_h_execute', 'b_c_execute', 'pledge_execute', 'member_execute',
            'branch_execute', 'spot_check_execute', 'abnormal_execute',
            ]
    executeB = ['stock_freeze_execute', 'stockholder_change_execute']
    execute_d = ['c_mortgage_execute', 's_creditor_execute','mortgage_execute']
    url_home = "http://218.57.139.24"
    url_part_A = "/pub/gsgsdetail/"
    url_A = url_home + url_part_A + id_list["enttype"] + "/" + id_list["encrptpripid"]
    url_part_B = "/pub/sfgsdetail/"
    url_B = url_home + url_part_B + id_list["enttype"] + "/" + id_list["encrptpripid"]#菏泽市腾讯信息传播有限公司
    pool = Pool()

    # 司法协助公示信息
    pageSoup_B = get_html(url_B, {})
    if pageSoup_B != None:
        for c in executeB:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] = getattr(pool, c)(id_list, pageSoup_B)
            # common.for_print(result_B)

    # # 工商公示信息
    pageSoup_A = get_html(url_A, {})
    # if pageSoup_A != None:
    #     for c in executeA:
    #         print "%r %r %r" % ("*" * 20, c, "*" * 20)
    #         result[conf.tableDict[c]] = getattr(pool, c)(id_list, pageSoup_A)
    #         common.for_print(result_A)

    #
    # 以下是获取详情html的
    detailPage(pageSoup_A, id_list, execute_d)
    return result


if __name__ == '__main__':
    Tlist = [
    # {"encrptpripid": "3818255132abb96bab458bcfa143e36c", "entname": "济南腾讯科技有限公司", "enttype": "1130",
    #   "enttypename": "法定代表人:", "estdate": "2004年03月04日", "lerep": "桑圣羡", "pripid": "3701002817414",
    #   "regno": "913701027591892671", "regorgname": "济南市历下区市场监督管理局", "uniscid": "913701027591892671"},#济南腾讯科技有限公司 (股东，变更信息)
    #     {u'encrptpripid': u'6ec12b6d27818d6d5b5cd19062b2d7be',
    #      u'entname': u'\u9752\u5c9b\u5564\u9152\u6d77\u4e30\u4ed3\u50a8\u6709\u9650\u516c\u53f8', u'enttype': u'6110',
    #      u'regorgname': u'\u9752\u5c9b\u5e02\u9ec4\u5c9b\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
    #      u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'91370211743969779Q', u'lerep': u'\u9a6c\u5b81',
    #      u'pripid': u'3702004010425', u'estdate': u'2002\u5e7412\u670819\u65e5', u'uniscid': u'91370211743969779Q'},# 青岛啤酒海丰仓储有限公司（主要人员）
    #     {u'encrptpripid': u'e883ec8a87aa6c418fe456618faf72b5',
    #      u'entname': u'\u9752\u5c9b\u5e02\u5e73\u5ea6\u4ebf\u4e30\u5efa\u6750\u7535\u5668\u6709\u9650\u516c\u53f8',
    #      u'enttype': u'1130', u'regorgname': u'\u5e73\u5ea6\u5e02\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
    #      u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'370283228003719',
    #      u'lerep': u'\u6f58\u5fe0\u6cfd', u'pripid': u'1983082600219', u'estdate': u'1997\u5e7405\u670808\u65e5',
    #      u'uniscid': u''},  # 青岛市平度亿丰建材电器有限公司（分支机构，经营异常，抽查检查）
    #     {u'encrptpripid': u'5f0883bcfc96652900778c9d9439fb6b',u'entname': u'\u9752\u5c9b\u82b3\u6797\u4fe1\u606f\u6280\u672f\u6709\u9650\u516c\u53f8', u'enttype': u'1130',
    #      u'regorgname': u'\u9752\u5c9b\u5e02\u5e02\u5357\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:',
    #      u'regno': u'913702026790575048',u'lerep': u'\u5218\u65b9\u660e', u'pripid': u'370202230018585', u'estdate': u'2008\u5e7408\u670822\u65e5',
    #      u'uniscid': u'913702026790575048'},  # 青岛芳林信息技术有限公司(首页翻页，股权出质)
        {u'encrptpripid': u'6521eed6b26b037f4b8c68963a80f63c',
         u'entname': u'\u9752\u5c9b\u8d5b\u6210\u5546\u8d38\u6709\u9650\u516c\u53f8', u'enttype': u'1151',
         u'regorgname': u'\u9752\u5c9b\u5e02\u57ce\u9633\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'370214230159832',
         u'lerep': u'\u5305\u8d5b\u82b1', u'pripid': u'370214230159832', u'estdate': u'2014\u5e7407\u670825\u65e5',
         u'uniscid': u''},  # 青岛赛成商贸有限公司

        {u'encrptpripid': u'e761cc62cdbdf16b4599f5454ed04d89',
         u'entname': u'\u57ce\u9633\u533a\u5fb7\u96c5\u8f69\u5de5\u827a\u54c1\u914d\u4ef6\u5546\u793e',
         u'enttype': u'9999',
         u'regorgname': u'\u9752\u5c9b\u5e02\u57ce\u9633\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u7ecf\u8425\u8005:', u'regno': u'370214600624916', u'lerep': u'\u6731\u5e86\u5a1f',
         u'pripid': u'370214600624916', u'estdate': u'2013\u5e7409\u670826\u65e5', u'uniscid': u''},  # 城阳区德雅轩工艺品配件商社

        {u'encrptpripid': u'f35353be30f58a233e95ea05941053f8',
         u'entname': u'\u9752\u5c9b\u5343\u8bed\u7f51\u7edc\u4fe1\u606f\u6280\u672f\u6709\u9650\u516c\u53f8',
         u'enttype': u'1151',
         u'regorgname': u'\u9752\u5c9b\u5e02\u9ec4\u5c9b\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'370211230123936',
         u'lerep': u'\u9648\u52a0\u8003', u'pripid': u'370211230123936', u'estdate': u'2013\u5e7411\u670814\u65e5',
         u'uniscid': u''},  # 青岛千语网络信息技术有限公司

        {u'encrptpripid': u'8193f4032ce2b0a89ccb5141e407d831',
         u'entname': u'\u9752\u5c9b\u4e09\u7965\u79d1\u6280\u80a1\u4efd\u6709\u9650\u516c\u53f8', u'enttype': u'5210',
         u'regorgname': u'\u9752\u5c9b\u5e02\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'9137020074720583XM',
         u'lerep': u'\u9b4f\u589e\u7965', u'pripid': u'3702004010851', u'estdate': u'2003\u5e7404\u670816\u65e5',
         u'uniscid': u'9137020074720583XM'},  # 青岛三祥科技股份有限公司

        {u'encrptpripid': u'ebf9b684b30d44010abef60df2663475',
         u'entname': u'\u9752\u5c9b\u6d77\u738b\u7eb8\u4e1a\u80a1\u4efd\u6709\u9650\u516c\u53f8', u'enttype': u'1229',
         u'regorgname': u'\u9752\u5c9b\u5e02\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'91370200264627202X',
         u'lerep': u'\u51b7\u7389\u559c', u'pripid': u'2000071400151', u'estdate': u'1994\u5e7406\u670820\u65e5',
         u'uniscid': u'91370200264627202X'},  # 青岛海王纸业股份有限公司

        {u'encrptpripid': u'316dc6f098945993b1c61577b30a48be',
         u'entname': u'\u9752\u5c9b\u4e39\u9999\u98df\u54c1\u6709\u9650\u516c\u53f8', u'enttype': u'5110',
         u'regorgname': u'\u9752\u5c9b\u5e02\u57ce\u9633\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'913702007875543991',
         u'lerep': u'\u738b\u6811\u658b', u'pripid': u'3702052806118', u'estdate': u'2006\u5e7403\u670830\u65e5',
         u'uniscid': u'913702007875543991'},  # 青岛丹香食品有限公司

        {u'encrptpripid': u'aa7a7874e4c318fdef9a9862c25f9cc7',
         u'entname': u'\u9752\u5c9b\u661f\u6cb3\u8054\u4fe1\u7f51\u7edc\u79d1\u6280\u6709\u9650\u516c\u53f8',
         u'enttype': u'1130',
         u'regorgname': u'\u9752\u5c9b\u5e02\u9ec4\u5c9b\u533a\u5de5\u5546\u884c\u653f\u7ba1\u7406\u5c40',
         u'enttypename': u'\u6cd5\u5b9a\u4ee3\u8868\u4eba:', u'regno': u'913702116903463157',
         u'lerep': u'\u8463\u8fde\u52cb', u'pripid': u'370211230021680', u'estdate': u'2009\u5e7408\u670812\u65e5',
         u'uniscid': u'913702116903463157'},  # 青岛星河联信网络科技有限公司

    ]

    for tag_list in Tlist:
        print tag_list["entname"]
        main(tag_list)
        # print "*******"
        # time.sleep(5)

