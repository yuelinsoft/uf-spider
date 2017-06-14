# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'jiangshu', 'anhui'
from common import conf,common
import requests
from bs4 import BeautifulSoup
import re
Session = requests.Session()
result = {}

# get_html 可以获取翻页的内容
def get_html(url1, list_, data_dict0):
    url0 = 'http://gsxt.xjaic.gov.cn:7001/'
    url = url0 + url1
    headers_info = {
        'Connection': 'keep-alive',
        'Host': 'gsxt.xjaic.gov.cn:7001/',
        # 'X-Forwarded-For':'8.8.8.8',
        # 'Referer':'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_pspc/pspc_queryCorpInfor_gsRelease.jsp',
        # 'Referer': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfor_gsRelease.jsp',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    }
    data = {
        'maent.pripid': list_[0],
        'random': '1471421122907'#
    }
    for key in data_dict0:
        data[key] = data_dict0[key]
    req = Session.post(url, headers=headers_info, data=data)
    content = req.text
    if len(content)<=150:
        return None
    soup = BeautifulSoup(content, 'lxml')
    return soup

def get_dict(pageSoup, *br_keyword, **d):
    # **d: get info
    # *br_keyword: get names and data, a tuple like this : ([]).
    try:
        info = pageSoup.find('table', id= d["id"])
        names=data=[]
        names = info.findAll('th')
        data = info.findAll('td')
    except:
        # print("Error: does not have this part.")
        return {}
    names_list = []
    data_list = []
    for name in names[1:]:
        names_list.append(name.text.encode('utf-8'))
    for d in data:
        data_list.append(d.text.strip().replace('\r\n', ''))
    if len(data_list) == 0:
        return {}
    dict_ba = dict(zip(names_list,data_list))
    # for d in dict_ba: print d, dict_ba[d]
    return dict_ba

def get_dict_2(pageSoup, *br_keyword):
    dict_ba = {}
    try:
        box = pageSoup.find(text=br_keyword[0]).find_parent('tr').next_siblings
    except:
        return dict_ba
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

def detailPage(list_, execute_d):
    url1 = 'ztxy.do'
    data_dict0 = {
        'method': 'dcdyInfo',
        'czmk' : 'czmk4'
                }
    pageSoup = get_html(url1, list_, data_dict0)
    info = pageSoup.find(id = 'table_dc')
    data = info.select('td a')
    p = '''doDcdyDetail\((.*?)\)'''
    aList = []
    for d in data:
        b = re.search(p, str(d))
        if b != None:
            s = b.group()
            aList.append(s.split("'")[1])
    if aList != []:
        url = 'ztxy.do'
        for xh in aList:
            data_dict0 = {
                'method': 'dcdyDetail',
                'maent.xh': xh
            }
            pageSoup_d = get_html(url1, list_, data_dict0)
            pool_d = Pool_d()
            for c in execute_d:
                print "%r %r %r"%("*"*20, c, "*"*20)
                result[conf.tableDict[c]] = getattr(pool_d, c)(pageSoup_d)
                # common.for_print(result_D)

class Pool():
    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'qyInfo',
            'maent.entbigtype':list_[1]
        }
        pageSoup = get_html(url1, list_, data_dict0)
        dict_ba = get_dict(pageSoup, '', id='baseinfo')
        if dict_ba != {}:
            dict_ba = common.basicinfo_dict(dict_ba,u'新疆')
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'jyycInfo',
            'czmk' : 'czmk6'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'reason','date_occurred','reason_out','date_out','authority']
        br_keyword = "table_yc"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚###
    def adm_punishment_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'cfInfo',
            'czmk': 'czmk3'
        }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authirty', 'pun_date', 'gongshiriqi', 'xiangqing']
        br_keyword = "table_gscfxx"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'qyInfo',
            'maent.entbigtype':list_[1]
        }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['reason', 'before_changes', 'after_changes', 'date_to_changes']
        br_keyword = "table_bg"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'baInfo',
            'czmk' : 'czmk2'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao','company_num','company_name','authority']
        br_keyword = "table_fr2"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要成员信息）
    def member_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'baInfo',
            'czmk' : 'czmk2'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao','person_name','p_position']
        br_keyword = "table_ry1"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'dcdyInfo',
            'czmk' : 'czmk4'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao','mortgage_reg_num','date_reg','authority','amount','status','gongshiriqi','xiangqing']
        br_keyword = "table_dc"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息###
    def pledge_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'gqczxxInfo',
            'czmk' : 'czmk4'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao','reg_code','pleder','id_card','plede_amount','brower','brower_id_card','reg_date','staues','gongshiriqi','changes']
        br_keyword = "table_gq"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'qyInfo',
            'maent.entbigtype':list_[1]
        }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'xiangqing']
        br_keyword = "table_fr"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'ccjcInfo',
            'czmk' : 'czmk7'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao','authority','spot_type','spot_date','spot_result']
        br_keyword = "table_ccjc"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息
    def stock_freeze_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'specificQuery': "commonQuery",
                    'propertiesName': "gqdjList"
                    }
        info = get_html(url1, list_, data_dict0)
        return info

    # QYXX_STOCKHOLDER_CHANGE股权更变信息
    def stockholder_change_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'specificQuery': "commonQuery",
                    'propertiesName': "gdbgList"
                 }
        info = get_html(url1, list_, data_dict0)
        return info

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, list_):
        url1 = 'ztxy.do'
        data_dict0 = {
            'method': 'yzwfInfo',
            'czmk' : 'czmk14'
                    }
        pageSoup = get_html(url1, list_, data_dict0)
        key_list = ['xuhao','reason_in','date_in','reason_out','date_out','authority','xiangqing']
        br_keyword = "table_wfxx"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        return dict_ba_list

class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        br_keyword = u"动产抵押登记信息"
        dict_ba = get_dict_2(pageSoup, br_keyword)
        dict_ba = common.c_mortgage_dict(dict_ba)
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        number = 5
        br_keyword = u"被担保债权概况"
        dict_ba = get_dict_2(pageSoup, br_keyword)
        dict_ba = common.s_creditor_dict(dict_ba)
        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0]['mortgage_reg_num']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):
        key_list = ['xuhao','mortgage_name','belongs','information','mortgage_range']
        br_keyword = "table_dywgk"
        dict_ba_list = common.get_dict_list(pageSoup, key_list, br_keyword)
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

def main(id_list):
    # # executeX中还没有进行数据库测试的,已经设置了在数据不会空时，raise error。
    executeA = [
        'basicinfo_execute', 'b_c_execute', 'adm_punishment_execute', 'member_execute','s_h_execute',
        'pledge_execute', 'mortgage_basic_execute','branch_execute', 'abnormal_execute',
        'spot_check_execute', 'black_info_execute'
              ]
    executeB = ['stock_freeze_execute','stockholder_change_execute']# 这个还没有验证
    execute_d = ['s_creditor_execute','mortgage_execute','c_mortgage_execute']
    # for t in id_list[1].split(","):
    tag_list = map(lambda i:i[1:-1],(id_list[1].split(",")))
    pool = Pool()
    for c in executeA:
        print "%r %r %r"%("*"*20, c, "*"*20)
        result[conf.tableDict[c]] =  getattr(pool, c)(tag_list)
        # common.for_print(result_A)

    # 以下是获取详情html的
    detailPage(tag_list, execute_d)
    return result


if __name__ == '__main__':
    # tag_list = ['\xe5\x92\x8c\xe7\x94\xb0\xe5\xb8\x82\xe4\xbd\xb3\xe5\x85\xb0\xe8\x85\xbe\xe8\xae\xaf', "'6532013000873290','50','K'"]
    # tag_list = ['', "'6523283000000082','50','K'"]# 木垒县阿里超市，变更信息（翻页），行政处罚
    # tag_list = ['',"'6500040000846554','11','K'"]# 新疆中润石油天然气股份有限公司，主要人员，股东信息
    tag_list = ['',"'6527240000002880','11','K'"]# 阿拉山口地平线石油天然气股份有限公司，动产抵押，股权出质
    # tag_list = ['',"'6500000016025212','11','K'"]# 新疆八一钢铁股份有限公司，分支机构
    # tag_list = ['',"'6501030000326853','11','K'"]# 乌鲁木齐广兴圣矿业有限公司，经营异常，抽查检查
    # tag_list = ['',"'6527000000354697','11','K'"]# 新疆宏顺达投资有限公司，严重违法
    main(tag_list)




