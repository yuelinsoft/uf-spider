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
        'Host' :'http://211.141.74.198:8081',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
            }
    b = None
    while b == None:
        req = Session.get(url, timeout=140, headers=headers_info)
        html = req.text
        print url,html
        p = r"\w{40}"
        b = re.search(p,str(html))
    robotcookieid =  b.group()
    headers_info = {
        'Connection': 'keep-alive',
        'Host' :'http://211.141.74.198:8081',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
            }
    if para[0]!={}:
        data = para[0]
        req = Session.get(url, timeout=40, headers=headers_info, data=data)
    else:
        cookies = {
            'ROBOTCOOKIEID':robotcookieid
                    }
        req = Session.get(url, timeout=40, headers=headers_info, cookies=cookies)
    content = req.text
    # print "more:",content
    if len(content)<=1024:# 这里可以再完善
        return None
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_html_2(url1, list_, pageSoup, data_dict0):
    # 未完善，需要token，referer，cookies
    token = ""
    dict_ba_list = []
    url0 = 'http://211.141.74.198:8081/aiccips'
    if url1 == "/pub/ccjcxx/" or url1 == '/pub/gsgqcz/':
        url = url0 + url1
    else:
        url = url0 + url1 + list_["enttype"]
    p = '''content=.*'''
    b = re.search(p,str(pageSoup.findAll('meta')[3]))
    if b != None:
        s = b.group()
        token = s.split('"')[1]
    url_A = "http://211.141.74.198:8081/aiccips/pub/gsgsdetail/" + list_["enttype"] + "/" + list_["encrptpripid"]
    headers_info = {
        'Connection': 'keep-alive',
        'Host' :'211.141.74.198:8081',
        'Accept-Encoding':'gzip, deflate',
        'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept':'application/json, text/javascript, */*; q=0.01',
        'X-CSRF-TOKEN':token,#"9c388421-a951-4c1b-8949-2e946a9d872a" ,
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer':url_A
    }
    data = {'encrpripid': str(list_['encrptpripid'])}
    for key in data_dict0:
        data[key] = data_dict0[key]
    cookies = {
            'JSESSIONID':'9617C50E2D1103CA22C0BB7EFB375769',
            'CNZZDATA1000300906':'1634309238-1471219644-http%253A%252F%252Fgsxt.saic.gov.cn%252F%7C1471835487',
            'SECSESSIONID':'3e00eea2ac30cdb840ad210873c1996c',
            'ROBOTCOOKIEID':'6fcad1cf858e8da4378fbff03f74766e0e3ed7a2'
    }#  需要cookies，可能要从前面的页面获取。
    print url
    req = Session.post(url, timeout=40, headers=headers_info, data=data, cookies=cookies)
    content = req.text
    print content
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
            dict_ba = common.basicinfo_dict(dict_ba,u'吉林')
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
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(dlink, pageSoup)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

def main(id_list):
    executeA = ['basicinfo_execute','member_execute'#'s_h_execute',
            # 'mortgage_basic_execute','adm_punishment_execute','black_info_execute',
            # 'b_c_execute',  'b_c_execute', 'pledge_execute',
            # 'branch_execute', 'spot_check_execute', 'abnormal_execute',
            ]
    executeB = ['stock_freeze_execute', 'stockholder_change_execute']
    execute_d = ['c_mortgage_execute', 's_creditor_execute','mortgage_execute']
    url_home = "http://211.141.74.198:8081/aiccips"
    url_part_A = "/pub/gsgsdetail/"
    url_A = url_home + url_part_A + id_list["enttype"] + "/" + id_list["encrptpripid"]
    url_part_B = "/pub/sfgsdetail/"
    url_B = url_home + url_part_B + id_list["enttype"] + "/" + id_list["encrptpripid"]
    pool = Pool()

    # 司法协助公示信息
    pageSoup_B = get_html(url_B, {})
    if pageSoup_B != None:
        for c in executeB:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] = getattr(pool, c)(id_list, pageSoup_B)
            # common.for_print(result_B)

    # 工商公示信息
    pageSoup_A = get_html(url_A, {})
    if pageSoup_A != None:
        for c in executeA:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] = getattr(pool, c)(id_list, pageSoup_A)
            # common.for_print(result_A)

    # 以下是获取详情html的
    # detailPage(pageSoup_A, id_list, execute_d)
    return result


if __name__ == '__main__':
    Tlist = [
            {
                "encrptpripid": "cb1849d8270c3feb0da4735af52cd39c5c9d73af0b028163c80387ef8c6fbcf06a702e8d10b085495ec8c13f602a5f35",
                "entname": "吉林市旬杨经贸有限责任公司", "enttype": "1130", "enttypename": "", "estdate": "0005-08-31",
                "lerep": "刘妍", "pripid": "57894a00-5e9d-46e5-b969-610511bec829", "regno": "2202002105315",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市旬杨经贸有限责任公司
            {
                "encrptpripid": "5168c8350f50f54a7f18a35a47c9dcb57da9792c95fea3d0c2ea818fe48a5af72f1eae8a3f292d10aebe9eb402fa89e7",
                "entname": "吉林高新区敦霞烟床", "enttype": "9999", "enttypename": "", "estdate": "0199-06-10", "lerep": "孙敦霞",
                "pripid": "c55c7cb3-91ee-4c08-9b74-f16eb25a9801", "regno": "2202003011177",
                "regorgname": "吉林市工商行政管理局高新开发区分局", "uniscid": ""},  # 吉林高新区敦霞烟床
            {
                "encrptpripid": "07357460c4f9af31362a2a42a351006200608d819a3d0ce785a9f04c3100fdb5815af17e04c5324e8d02f674707a79b7",
                "entname": "吉林市丰满区宏业酱菜厂", "enttype": "9999", "enttypename": "", "estdate": "0203-12-09", "lerep": "杜君",
                "pripid": "884a67dc-0631-4177-bfbe-0d329212c0af", "regno": "2202113201876",
                "regorgname": "吉林市工商行政管理局丰满分局", "uniscid": ""},  # 吉林市丰满区宏业酱菜厂
            {
                "encrptpripid": "f2b84759cdf733aac85f03b35fe72102579cbf5572e79f3e2fc14fe74871a1bce96ad5e7e1c09972627d4ecd77838563",
                "entname": "吉林市吉化高科技实业公司", "enttype": "3200", "enttypename": "", "estdate": "0994-05-12",
                "lerep": "宫利民", "pripid": "52115c47-4427-4903-88c2-d648b00fee7d", "regno": "2202001001589",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市吉化高科技实业公司
            {
                "encrptpripid": "637c32447a3ee584c334d8c46e724a5e5796c416b42db97508bb2c7a7d61d11676ef8a9e1d5504d6b0535a03ae07781a",
                "entname": "吉林省广播影视器材商场", "enttype": "3000", "enttypename": "", "estdate": "0997-04-19", "lerep": "孙步军",
                "pripid": "e8c037cf-10f4-4369-8935-55d017533651", "regno": "24381370-0", "regorgname": "吉林省工商行政管理局",
                "uniscid": ""},  # 吉林省广播影视器材商场
            {
                "encrptpripid": "a7f0d0f50d4ac28d3914eebc7a4dca8c0ecfd7339341eda9f12ed9809699c89763e571cfa3f506970d2d9093a2753c02",
                "entname": "吉林省敬峰物业有限公司", "enttype": "1100", "enttypename": "", "estdate": "1005-10-31", "lerep": "田兴",
                "pripid": "55331d9e-8b77-4e3e-958c-b51c4486b677", "regno": "24380073-1", "regorgname": "吉林省工商行政管理局",
                "uniscid": ""},  # 吉林省敬峰物业有限公司
            {
                "encrptpripid": "148ff2a25076bffd35333175fbd9479b07e014fb3100496ec6aef32fab9a4b2f118d976c70211d002837418b92d9e9da",
                "entname": "吉林市金属材料总公司优钢公司", "enttype": "3100", "enttypename": "", "estdate": "1199-03-11",
                "lerep": "赵顶昌", "pripid": "aef94269-734e-4358-b97b-db09739b9f8a", "regno": "12454098",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市金属材料总公司优钢公司
            {
                "encrptpripid": "b33d21c2aff6143bb952f0576ca1b2b8ba2e63c07f99210511148985114e63d8b0145a49c29e4703522a40aa167e4cfd",
                "entname": "吉林市铁联蓄电池经销部", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "舒大忠",
                "pripid": "1249dfde-79a9-48a5-bbbf-a4fbca0c6409", "regno": "12447605", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市铁联蓄电池经销部
            {
                "encrptpripid": "d0c2a8415d4b54cba26dd14ecca336d4d61ba0fef8281cf84108b3316b8420455047786944fdcaee09a9c9f2937cedc4",
                "entname": "吉林市永乐日化产品分装厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "邹长连", "pripid": "70a8777d-7b85-443d-a6c4-bacb477b3cae", "regno": "12447550",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市永乐日化产品分装厂
            {
                "encrptpripid": "afed73a72556a15d0da02145b3664de1376640ea791c509d5ff39c6c28a792e112204917ab6bb15893c4053123341352",
                "entname": "吉林市鼓风机厂丰功风机经销部", "enttype": "4000", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "贾孝言", "pripid": "3cc4d6c3-45c5-4744-95b7-a225c97b2780", "regno": "82452002",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市鼓风机厂丰功风机经销部
            {
                "encrptpripid": "22e04634acc1fc61111a122e0d941c709e2d988315eb5b5addcb25a5a9c2100b0221e942668030e2d4a69eb253fb40e2",
                "entname": "吉林市红旗轮胎经销公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "周占义",
                "pripid": "d9b2d831-ad05-47d4-986d-c217770ee673", "regno": "12452618", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市红旗轮胎经销公司
            {
                "encrptpripid": "969e21792ca76e426b6f8bde316697de26eee863cbbde029275aff84c31abe674a660d1c7e64ca5d98bb904a61e83c0a",
                "entname": "吉林市腾飞建材商店", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "王会艳",
                "pripid": "8f24e05e-d886-4ea5-8cf2-c856408c457e", "regno": "12449703", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市腾飞建材商店
            {
                "encrptpripid": "a1204bfddb4a462297c0a63943e5dd5a7f67dc9bdb7fd19734a093d9af44632b2f7dba9906005c56128a68d5dde907f2",
                "entname": "吉林市鑫宇五交化商店", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "于默然",
                "pripid": "0449917b-8c48-4708-849c-4dfab12ec77a", "regno": "12451106", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市鑫宇五交化商店
            {
                "encrptpripid": "3582889a7691e3b85e49ffc751552f5c5aec4f7b3ff727e921a0dd86c8eb1b57ba533cd5ec73fcd8c3145e0553a2e0a9",
                "entname": "吉林市建新汽车配件经销部", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "11",
                "pripid": "ee98357f-90e4-445d-baf9-9803f638b5aa", "regno": "12448458", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市建新汽车配件经销部
            {
                "encrptpripid": "7c0cfc5a5b20e5360d524c5f81cb276ceffe4f2ef13ed03deae6d4f9a82a8b5f57c6447a240099597cd5a4ae23116106",
                "entname": "吉林市拓达神大酒店", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "周雷",
                "pripid": "36e56719-be77-445f-ac44-385c0eef17de", "regno": "12450612", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市拓达神大酒店
            {
                "encrptpripid": "a4a7947b11ac4ca9b94711d0186a4b54c2dd72fa3901ef6f44aeb046be2960842d86599187108a1a5b68134e087d967d",
                "entname": "吉林市兴隆油脂化工厂", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "齐克",
                "pripid": "4eb730a7-fda6-4ce6-ba70-73c0ad55b0f0", "regno": "12452189", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市兴隆油脂化工厂
            {
                "encrptpripid": "1cb7e81a225dd8b64a4f32f123a21ae3fc76008042d666d7acacac34dbea96901339bc7dcaffdba1fed077b1c914a1d2",
                "entname": "吉林市炭素工业气体实业公司", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "董海成", "pripid": "9d4b43c9-9b8d-4c0f-aa69-57cf4e121f8c", "regno": "12452011",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市炭素工业气体实业公司
            {
                "encrptpripid": "ddf61ec7d29ef02404cb1b549ad59a91d8821cdd681ddf6f95100d54199f29784d32c5691d0af4d13c1e8c7dece59d7a",
                "entname": "吉林市临江化工经销处／吉林市昌海五交化经销处", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "石昌德", "pripid": "ffe03629-d239-4bec-841a-faf40f1d7470", "regno": "12450445",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市临江化工经销处／吉林市昌海五交化经销处
            {
                "encrptpripid": "fdbfede4d0b0c2483c5a56aa66613fa809057ce9de7fe8d35c1d0226bafd0a3e2a77f669cd7aed564d7e065330eb119c",
                "entname": "地质矿产部吉林石油普查勘探指挥所劳动服务公司惠美理发店", "enttype": "4320", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "吴立群", "pripid": "d733ece7-bd60-4eef-b057-ae6901525635", "regno": "82400832",
                "regorgname": "长春市工商行政管理局", "uniscid": ""},  # 地质矿产部吉林石油普查勘探指挥所劳动服务公司惠美理发店
            {
                "encrptpripid": "a8b0b4d8a01afd0e5b5750d61708a3c991594ccb04c682634ade6c7bc98402c09a490a22b007211f28ee698d9488fa4f",
                "entname": "中国人民解放军武装警察部队吉林市森警支队军人服务社", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "李永军", "pripid": "408d2b13-3a58-468c-94c3-b05aa95183ec", "regno": "12447193",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 中国人民解放军武装警察部队吉林市森警支队军人服务社
            {
                "encrptpripid": "ee2fec23e584fe929742b7e6ede5c8206547f6a208d0cd25463ace39547e2f16252af915767058da08fcb0928c02f1fd",
                "entname": "吉林市兴林农副产品经营部", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "丁德林", "pripid": "df8bed49-8bce-4303-b801-50eb0d4af703", "regno": "12448745",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市兴林农副产品经营部
            {
                "encrptpripid": "64b4ef370c29a62ab1af05ae597db62becc37e9618b1ffa8b05f15dfa19fb304a4c567b2d075672cb73f47ceade7f536",
                "entname": "吉林市红伟建材经销部", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "杨喜田",
                "pripid": "1c3f8214-1222-4212-9822-191da09afe5a", "regno": "12451675", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市红伟建材经销部
            {
                "encrptpripid": "fd87672da990d9757ffc56471f53b564bdd38a6691538bd77ea8d9db84261ee7c920fef11c402a0313549bf57eb41629",
                "entname": "吉林市银嘉科技公司", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "朱礼春",
                "pripid": "c6780b23-0125-42e8-aeec-22f061dd13c8", "regno": "12451785", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市银嘉科技公司
            {
                "encrptpripid": "d0f9d047481d70ea14bd95f07e72ffefaf5a15191a3d5fa431d2405e68e063f3cd1f03a599b80c7fa5831ccea489e13e",
                "entname": "吉林市祥云木材经销公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "张孟良",
                "pripid": "8397ba03-98d7-4246-aca4-b45b20527840", "regno": "12453069", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市祥云木材经销公司
            {
                "encrptpripid": "abe2e6369cbec5ab6efef44a0fe9cca1465490aa60b604711154fea254928c320a80e68b141d641b1eacfb961bbf72af",
                "entname": "沈阳铁路局吉林汽车运输公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "曲鹤龄", "pripid": "b5eedf84-71e2-4b29-b307-d3b780d10340", "regno": "12447502",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 沈阳铁路局吉林汽车运输公司
            {
                "encrptpripid": "1474ae7bd8351b048d1751f47073f90df8efec6f6885d3c7efa63a5493d0af25714cf071d18e8cda826c70cb39ac87b2",
                "entname": "吉林市江城染料分装厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "刘久华",
                "pripid": "9c713399-5449-4a46-af6e-2a4e5aabdbde", "regno": "12449722", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市江城染料分装厂
            {
                "encrptpripid": "b4697d547e27ae160805074576f4cfb1cd7d7bf9d283caaddb12f8aea2e5f201bbea6ffe0e3eb5edc08e7ca20906124a",
                "entname": "吉林市冶金经销公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "王赫",
                "pripid": "68d600a9-f22a-43b7-a012-2c2fbb789a00", "regno": "12451918", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市冶金经销公司
            {
                "encrptpripid": "f86930e2354ecc5c22d73cc2b09cd8a21d269558e5b9fce58d4016129974caa75468230c5b3429f6b75d5500c0b08f41",
                "entname": "吉林市外商投资企业公司经营处", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "李昌荣", "pripid": "661541d7-fd75-4f7b-8868-d72e6b73a192", "regno": "12451891",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市外商投资企业公司经营处
            {
                "encrptpripid": "530e2574db17170e66431a5e63d1559f6e26cc918e1f568aaba8919a199bdfa3650944a6bebf5820a2183b80d6d1bb37",
                "entname": "吉林市宇源五交化经销部", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "刘智戎",
                "pripid": "e5978b0f-ef8d-496e-a382-0d013e2444d9", "regno": "12451845", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市宇源五交化经销部
            {
                "encrptpripid": "1601a3d58d1a56f7b181122d49f8a483c9f8391cddeac5cfe8f5a2dfe6dd7f45c537d5557d0087e983f8149867105e2c",
                "entname": "吉林市延中现代化办公用品公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "王晓东", "pripid": "2396fca8-2204-4af9-a569-b93ce578451e", "regno": "12453185",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市延中现代化办公用品公司
            {
                "encrptpripid": "5a658a607295e2943c5bac539a8e5b4fc004cf56beac27fcaad297ab1bfb81279c7a38c8b8d20b3540ea7e5de3b0dc6f",
                "entname": "吉林省生物制品厂供销公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "张俊",
                "pripid": "4d5f5fd9-759a-4e1c-9957-2bf01137a4c3", "regno": "12451009", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林省生物制品厂供销公司
            {
                "encrptpripid": "44af41060b9bbbc655ed9d4d20b2c855ad5266024e95f99b5e2355ba10b5c070dc0aa4b1a2372f16e3bb2f8d6851c8b8",
                "entname": "吉林市红九印刷厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "吴亚芹",
                "pripid": "92467d0f-da27-4a58-9ab8-9d66d81fc26c", "regno": "12451025", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市红九印刷厂
            {
                "encrptpripid": "ef293b5cbab6e02fce742fdd5aacc00e36fb874f29dc6bbd63206c78b1dd6ab62d09f29fad8debe424abc388dd0519d4",
                "entname": "吉林市东联金属材料经销公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "于占水", "pripid": "1e1347dd-69b2-48a6-affa-3431c505f8dd", "regno": "12451051",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市东联金属材料经销公司
            {
                "encrptpripid": "2c160cf1fae078df04c3407f1155ea86c06c124995f297faf029e08a6cd5fb82798c190d9c9e1b2c5f1a8e4a768c4c38",
                "entname": "吉林市港华贸易公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "王作成",
                "pripid": "2861eb1a-5d93-4dcd-93ab-36edd923a9cd", "regno": "12451050", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市港华贸易公司
            {
                "encrptpripid": "2e2dd2ea3a49fb184d399c8d2e9907eece07b4eddcb7471669b490bd8221224d3282beaf033e21a7a4cf5cba499afa3e",
                "entname": "吉林市豆利宝冷饮制品厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "温玉亭",
                "pripid": "2b06888f-c706-417b-9363-bc23dfde34ae", "regno": "12449813", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市豆利宝冷饮制品厂
            {
                "encrptpripid": "acae187e292ccfea47f140eecd3394857c35f29f37cca05896d231d6417476b2f940b0c8a8968892390259235cb69581",
                "entname": "吉林市城南制材厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "程海军",
                "pripid": "cba516f7-825d-420c-868c-22631d9dc643", "regno": "12450624", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市城南制材厂
            {
                "encrptpripid": "a21d96b9f5139e87577d6c99bd51a41bac8121473f4872893d3d3190edea148c42be17187524098fb7aea85830a1ee58",
                "entname": "吉林市卫达经济技术开发公司", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "潘树森", "pripid": "e1ae97d5-f867-4997-aece-45dc5c61d633", "regno": "12447005",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市卫达经济技术开发公司
            {
                "encrptpripid": "1c652d6de730cb21947f692e8b8bbae126a90baef195dee51a300d2222a95ece4131dd4715fd88e580580dcaee833d7e",
                "entname": "吉林市王冠装饰装璜配套公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "张权福", "pripid": "1d42c1e6-0946-43ae-8fa0-1b6fc2d1a121", "regno": "12447323",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市王冠装饰装璜配套公司
            {
                "encrptpripid": "33ffc5ae6ad05161a5d1bcd9be7111c98184e458731fd9e039d403feb4048bd4ad26519fc69b35c45e68b18f4567880f",
                "entname": "吉林市江南金属材料经销处", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "付宝权", "pripid": "6689ae54-43ac-4edf-8fe9-46c053024d6f", "regno": "12450643",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市江南金属材料经销处
            {
                "encrptpripid": "1edc8aa74a492c5da4244ccbb5a2f1bd2b41cd9f5869134cf894953381fb8ff8d654ce6369dec060c04c40401cdf9733",
                "entname": "吉林市江城锁店", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "阮凤山",
                "pripid": "f1ebb157-b506-436a-b3e4-b0129f280d04", "regno": "12450646", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市江城锁店
            {
                "encrptpripid": "42b0e359a3f97f19dba14db693f4c26e4ac5ee8c1517cff97c4f90b423503002ef33c88f792ffbb1925ddfef1a68e185",
                "entname": "吉林市清泉饮料经销部", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "高洪勋",
                "pripid": "44b17984-a09d-433c-837c-e69c785fb414", "regno": "12452141", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市清泉饮料经销部
            {
                "encrptpripid": "1229730292e62a9fe07094be03e87f1d9b852de4705822e94b3dc6495022f817e4cda9158c6a50acd36f0eda5551208d",
                "entname": "吉林市凌山技术开发公司", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "吴忠义",
                "pripid": "d5df9018-e771-4c3e-a856-e37b654e6552", "regno": "12452249", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市凌山技术开发公司
            {
                "encrptpripid": "63d7944e5da8a50fe9137a39808c38d15ecb40da4a3e69ca40621ce2fe1634eed61234c56efee352147843c786b2b7ea",
                "entname": "吉林市信达美发用品制造厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "孙永德", "pripid": "d37e4bc2-aff1-4c06-96f7-61ba95130de8", "regno": "12450250",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市信达美发用品制造厂
            {
                "encrptpripid": "71c4de0f25c414d33c269f137f398e06f2433f69e406d1f923382fd7aae162f7cac81ff76d4b08ade0148944485d1ee9",
                "entname": "吉林市松花饮料厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "孙德军",
                "pripid": "64d295f9-7b99-4734-ba6c-e3ec3a4d0ad7", "regno": "12449711", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市松花饮料厂
            {
                "encrptpripid": "f387e56cdd39f0ead23b603d9d5de50818c0730656aad789c0e3a8bb800f56e9ba1a0a435f1e3955d2c367c1ee2d6048",
                "entname": "吉林市江怀五交化商店", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "许教海",
                "pripid": "549e65d8-90e5-4a96-a18e-7bdb0cb2fac2", "regno": "12447890", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市江怀五交化商店
            {
                "encrptpripid": "01784fa2b7d1ace9e19db63bb6276e16c4615b97a32caa83b630a5a29cc261bd2f039bbbf187e017f0e9285956cb9b90",
                "entname": "吉林市利师无尘粉笔厂", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "李凤霞",
                "pripid": "cfd734d7-52b1-4b85-aac1-6476b3c97ad4", "regno": "12451538", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市利师无尘粉笔厂
            {
                "encrptpripid": "3e7176353462bfab6f018d5b5bb45ee6c8882c784e678ff5a85f43e18da49511e5ae9c0237bc2fe5b46bd2f43c67a285",
                "entname": "吉林市干调食杂采购供应站", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "葛全生", "pripid": "91ba46f9-b1f3-4625-a098-df7a3cf5bfe3", "regno": "12448446",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林市干调食杂采购供应站
            {
                "encrptpripid": "8af2e6c3cc027d9f101f1a3cc4e7a610703321188f6dbff9f9068b858a4c2903cd7a37e37109439ded6b8bfcfff0b8be",
                "entname": "吉林手表工业公司技协服务部", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30",
                "lerep": "任国吉", "pripid": "6bc8b3c8-0364-4bda-b00b-943aef963fae", "regno": "12450233",
                "regorgname": "吉林市工商行政管理局", "uniscid": ""},  # 吉林手表工业公司技协服务部
            {
                "encrptpripid": "0c51b07942c05df865456cc4094f5fb3e4464b6e47acb25fe05571b3420a64f0cc4f853b6f5dd11cd165a732dc15a5f1",
                "entname": "吉林市水泥制品厂", "enttype": "3100", "enttypename": "", "estdate": "1899-12-30", "lerep": "陈世文",
                "pripid": "f72a1c11-6dc8-4feb-ade0-34424c6c2bd2", "regno": "12447504", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""},  # 吉林市水泥制品厂
            {
                "encrptpripid": "9a70b06039632e7ce376ef5c1a04132f8326ae843052257cfa494251a814e740de636eedf65ebf2067b713c22ce971b1",
                "entname": "吉林市西城副食品商店", "enttype": "3200", "enttypename": "", "estdate": "1899-12-30", "lerep": "王喜林",
                "pripid": "8286386f-fa94-4e9e-8e5f-a16f26abf734", "regno": "12450222", "regorgname": "吉林市工商行政管理局",
                "uniscid": ""}  # 吉林市西城副食品商店

    ]
    for tag_list in Tlist[:1]:
        print tag_list["entname"]
        main(tag_list)
        # print "*******"
        # time.sleep(5)

