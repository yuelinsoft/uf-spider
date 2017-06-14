# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'jiangshu'
from __future__ import unicode_literals
from EnterpriseCreditCrawler.common import common, conf
import requests
from bs4 import BeautifulSoup
import json
Session = requests.Session()
result = {}

'''
股权出质登记信息的获取方法有点特殊
'''

def mulColumn(listA):
    listB = []
    for d in listA:
        dnew1 = {}
        dnew2 = {}
        dnew1["VALUES1RN"] = d["VALUES1RN"]
        dnew1["PERSON_NAME1"] = d["PERSON_NAME1"]
        dnew1["POSITION_NAME1"] = d["POSITION_NAME1"]
        listB.append(dnew1)
        if d.has_key("VALUES2RN"):
            dnew2["VALUES1RN"] = d["VALUES2RN"]
            dnew2["PERSON_NAME1"] = d["PERSON_NAME2"]
            dnew2["POSITION_NAME1"] = d["POSITION_NAME2"]
            listB.append(dnew2)
    return listB

# get_html 可以获取翻页的内容
def get_html(url1, list_, data_dict0):
    url0 = 'http://www.jsgsj.gov.cn:58888/ecipplatform/'
    url = url0 + url1
    headers_info = {
        'Connection': 'keep-alive',
        'Host': 'www.jsgsj.gov.cn:58888',
        # 'X-Forwarded-For':'8.8.8.8',
        # 'Referer':'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_pspc/pspc_queryCorpInfor_gsRelease.jsp',
        'Referer': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_ci/ci_queryCorpInfor_gsRelease.jsp',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
    }
    data = {
        'corp_id': list_[1],
        'corp_org': list_[0],
        'corp_seq_id': list_[2],
        'pageNo': '1',
        'pageSize': '5',
        'showRecordLine': '1',
    }
    for key in data_dict0:
        data[key] = data_dict0[key]
    req = Session.post(url, headers=headers_info,
                            data=data,
                            proxies=_proxies)
    jsonA = json.loads(req.content)
    if isinstance(jsonA, list)==True:
        return jsonA
    if jsonA.has_key("items")==False:
        raise ValueError("jsonA is a dict but has not key [items].")
    if jsonA.has_key("total")==False:
        return jsonA["items"]
    total = int(jsonA["total"])
    lines = len(jsonA["items"])
    info = jsonA["items"]
    if total > lines:
        if divmod(total, lines)[1]!=0:
            page = divmod(total, lines)[0]+1
        else:
            page = divmod(total, lines)[0]
        for i in range(2,page+1):
            data['pageNo'] = str(i)
            req = Session.post(url, headers=headers_info,
                                    data=data,
                                    proxies=_proxies)
            jsonA = json.loads(req.content)
            info_0 = jsonA["items"]
            info = info + info_0
    return info

class Pool():
    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, list_):
        url = 'http://www.jsgsj.gov.cn:58888/ecipplatform/ciServlet.json?ciEnter=true'
        headers_info = {
            'Connection': 'keep-alive',
            'Host': 'www.jsgsj.gov.cn:58888',
            'X-Forwarded-For': '8.8.8.8',
            'Referer': 'http://www.jsgsj.gov.cn:58888/ecipplatform/inner_pspc/pspc_queryCorpInfor_gsRelease.jsp',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.155 Safari/537.36'
        }
        data = {
            'id': list_[1],
            'org': list_[0],
            'seq_id': list_[2],
            'specificQuery': "basicInfo"
        }
        req = Session.post(url,
                           headers=headers_info,
                           data=data,
                           proxies=_proxies)
        dict_keyword = {
            'company_name': [u'C2'],
            'fund_cap': [u'C6'],
            'company_type': [u'C3'],
            'check_type': [u'C13'],
            'authority': [u'C11'],
            'check_date': [u'C12'],
            'locate': [u'区域'],
            'owner': [u'C5', u'负责人', u'股东', u'经营者', u'执行事务合伙人', u'投资人'],
            'address': [u'C7', u'营业场所', u'经营场所', u'住所/经营场所'],
            'reg_num': [u'C1', u'注册号/统一社会信用代码'],
            'business_area': [u'C8', u'业务范围'],
            'start_date': [u'C4', u'注册日期'],
            'business_from': [u'C9', u'经营期限自']
        }
        dict_ba = json.loads(req.content)[0]
        dict_ba[u'区域'] = u'江苏省'
        dict_ba = common.judge_keyword(dict_ba, dict_keyword)
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {'propertiesName': "abnormalInfor"}
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'reason', 'date_occurred', 'juedinglierujiguan', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '作出决定机关（列入）', '移出异常原因', '移出日期', '作出决定机关（列出）']
        value_list = [['RN'], ['C1'], ['C2'], ['juedinglierujiguan'], ['C3'], ['C4'], ['C5']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_ADM_PUNISHMENT行政处罚###
    def adm_punishment_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {'propertiesName': "chufa"}
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority', 'pun_date', 'xiangqing']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','详情']
        value_list = [['RN'], ['C1'], ['C2'], ['C3'], ['C4'], ['C5'], ['xiangqing']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {'propertiesName': "biangeng"}
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        value_list = [['C1'], ['C2'], ['C3'], ['C4']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, list_):
        url1 = 'pspcServlet.json?pspcEnter=true'
        data_dict0 = {'specificQuery': "branchOfficeInfor"}
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        value_list = [['RN'], ['C1'], ['C2'], ['C3']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_MEMBER备案信息（主要成员信息）
    def member_execute(self, list_):
        url1 = 'ciServlet.json?ciEnter=true'
        data_dict0 = {
            'CORP_ID': list_[1],
            'CORP_ORG' :list_[0] ,
            'CORP_SEQ_ID' : list_[2],
            'specificQuery': "personnelInformation"
                    }
        info = get_html(url1, list_, data_dict0)
        dict_ba_list = mulColumn(info)#有两栏
        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']
        value_list = [['VALUES1RN'], ['PERSON_NAME1'], ['POSITION_NAME1']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
            'specificQuery': "commonQuery",
            'propertiesName': "dongchan"
        }
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority', 'amount', 'status', 'detail']
        # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'详情']
        value_list = [['RN'], ['C1'], ['C2'], ['C3'], ['C4'], ['C5'], ['C6']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_PLEDGE股权出质登记信息###
    def pledge_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'specificQuery': "commonQuery",
                    'propertiesName': "guquanchuzhi"
                    }
        info = get_html(url1, list_, data_dict0)
        if info != []:
            for i in info:
                data = BeautifulSoup(i["D1"], 'lxml').findAll('td')
                for d in range(len(data)):
                    i[str(d)] = data[d].text
                # print i['8']

        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '变化情况']

        value_list = [['0'], ['1'], ['2'], ['3'], ['4'], ['5'], ['6'], ['7'], ['8'], ['9']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in info:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, list_):
        url1 = 'ciServlet.json?ciEnter=true'
        data_dict0 = {
                    'CORP_ID': list_[1],
                    'CORP_ORG' :list_[0] ,
                    'CORP_SEQ_ID' : list_[2],
                    'specificQuery': "investmentInfor"
                    }
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type']
        # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型']
        value_list = [['C2'], ['C3'], ['C4'], ['C1']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'specificQuery': "commonQuery",
                    'propertiesName': "checkup"
                    }
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date', 'spot_result']
        # key_list = ['序号','检查实施机关','类型','日期','结果']
        value_list = [['RN'], ['C1'], ['C2'], ['C3'], ['C4']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_STOCK_FREEZE股权冻结信息
    def stock_freeze_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'specificQuery': "commonQuery",
                    'propertiesName': "gqdjList"
                    }
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number', 'status', 'xiangqing']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']
        value_list = [['NO_'], ['C1'], ['C2'], ['C3'], ['C4'], ['C5'], ['xiangqing']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_STOCKHOLDER_CHANGE股权更变信息
    def stockholder_change_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'specificQuery': "commonQuery",
                    'propertiesName': "gdbgList"
                 }
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'person', 'stock', 'person_get', 'court', 'xiangqing']
        # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']
        value_list = [['NO_'], ['C1'], ['C2'], ['C3'], ['C4'], ['xiangqing']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        return info_list

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, list_):
        url1 = ''
        dict_ba_list = {}#网页本身未有设置请求的参数
        if dict_ba_list != {}:
            raise ValueError("data_dict0 is not empty.")
        else:
            return []

class Pool_d():
    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'id': list_[1],
                    'org': list_[0],
                    'seq_id': list_[2],
                    'showRecordLine':'0',
                    'propertiesName': "dongchanDetail",
                    'specificQuery': "commonQuery"
                   }
        dict_ba = get_html(url1, list_, data_dict0)
        dict_ba_list = []
        if dict_ba != []:
            dict_ba = dict_ba[0]
            dict_ba['time_range'] = u'自' + dict_ba['C6'] + u'至' + dict_ba[u'C7']
            dict_keyword = {
                'mortgage_reg_num': [u'C1'],
                'date_reg': [u'C2'],
                'authority': [u'C3'],
                'mortgage_type': [u'C4'],
                'amount': [u'C5'],
                'time_range': [u'C7'],
                'mortgage_range': [u'C8']
            }
            dict_ba = common.judge_keyword(dict_ba, dict_keyword)
            # dict_ba = common.c_mortgage_dict(dict_ba)
            dict_ba_list.append(dict_ba)

        return dict_ba_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'id': list_[1],
                    'org': list_[0],
                    'seq_id': list_[2],
                    'showRecordLine': '0',
                    'propertiesName': "bdbzq",
                    'specificQuery': "commonQuery"
                   }
        dict_ba = get_html(url1, list_, data_dict0)
        dict_ba_list = []
        if dict_ba != []:
            dict_ba = dict_ba[0]
            dict_keyword = {
                'mortgage_type': [u'C1'],
                'amount': [u'C2'],
                'mortgage_range': [u'C3'],
                'time_range': [u'C4']
            }
            dict_ba = common.judge_keyword(dict_ba, dict_keyword)
            mortgage_reg_num = self.c_mortgage_execute(list_)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
            dict_ba_list.append(dict_ba)

        return dict_ba_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, list_):
        url1 = 'commonServlet.json?commonEnter=true'
        data_dict0 = {
                    'id': list_[1],
                    'org': list_[0],
                    'seq_id': list_[2],
                    'propertiesName': "dywgk",
                    'specificQuery': "commonQuery"
                     }
        dict_ba_list = get_html(url1, list_, data_dict0)
        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information', 'mortgage_range']
        # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']
        value_list = [['RN'], ['C1'], ['C2'], ['C3'], ['C4']]
        dict_keyword = dict(zip(key_list, value_list))
        info_list = []
        for dict_baa in dict_ba_list:
            dict_ba = common.judge_keyword(dict_baa, dict_keyword)
            info_list.append(dict_ba)

        # return info_list
        for dict_ba in info_list:
            mortgage_reg_num = self.c_mortgage_execute(list_)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return info_list

def main(**kwargs):
    tag_list = kwargs.get('id_tag')
    global _proxies
    _proxies = kwargs.get('proxies')
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时，raise error。
    executeA = [
        'black_info_execute','basicinfo_execute','abnormal_execute','adm_punishment_execute','b_c_execute',
        'branch_execute','member_execute','mortgage_basic_execute','pledge_execute',
        's_h_execute','spot_check_execute','stock_freeze_execute',
        'stockholder_change_execute'
              ]
    execute_d = ['c_mortgage_execute','s_creditor_execute','mortgage_execute']

    pool = Pool()
    for c in executeA:
        print "%r %r %r"%("*"*20, c, "*"*20)
        result[conf.tableDict[c]] = getattr(pool, c)(tag_list)
        # common.for_print(result_A)

    # 以下是需要获取详情html的
    url1 = 'commonServlet.json?commonEnter=true'
    data_dict0 = {
                'specificQuery': "commonQuery",
                'propertiesName': "dongchan"
                  }
    info = get_html(url1, tag_list, data_dict0)
    key = ["ORG", "ID", "SEQ_ID"]
    L = []
    for j in range(len(info)):
        list_ = []
        for key_i in key:
            list_.append(info[j][key_i])
        L.append(list_)

    c_mortgage = []
    s_creditor = []
    mortgage = []
    # 此处声明的三个变量是用于当有多个动产抵押项目的时候能把三个表的结果放到一个列表里面
    if L != []:
        pool_d = Pool_d()
        for list_ in L:
            # for c in execute_d:
            #     print "%r %r %r" % ("*" * 20, c, "*" * 20)
            #     result[conf.tableDict[c]] = getattr(pool_d, c)(list_)
            #     # common.for_print(result_D)
            print '*' * 20, execute_d[0], '*' * 20
            c_mortgage.extend(getattr(pool_d, execute_d[0])(list_))
            print '*' * 20, execute_d[1], '*' * 20
            s_creditor.extend(getattr(pool_d, execute_d[1])(list_))
            print '*' * 20, execute_d[2], '*' * 20
            mortgage.extend(getattr(pool_d, execute_d[2])(list_))
        result['qyxx_c_mortgage'] = c_mortgage
        result['qyxx_s_creditor'] = s_creditor
        result['qyxx_mortgage'] = mortgage
    else:
        result['qyxx_c_mortgage'] = c_mortgage
        result['qyxx_s_creditor'] = s_creditor
        result['qyxx_mortgage'] = mortgage

    return result


if __name__ == '__main__':
    # tag_list = ['1022', '70910911', '15']  # 江苏得厚软件科技有限公司（备案信息（主要成员信息））
    # tag_list = ['1022', '1034004', '14']  # 江苏省伟宇塑业有限公司（动产抵押登记信息（抵押物概况））
    # tag_list = ['1022', '84453764', '6']  # 江苏中超电缆股份有限公司（登记信息（更变信息））
    # tag_list = ['1022', '74111229', '5'] # 江苏文远生态农业科技有限公司（经营异常信息）
    # tag_list = ['1586','1422157','21'] # 南通综艺投资有限公司(股权冻结信息，股权更变信息，【翻页】）
    # tag_list = ['1586', '1138324', '28'] # 如东纺织橡胶有限公司（股权冻结信息，分支机构信息）
    # tag_list = ['1022', '64887518', '2'] # 绿点科技（无锡）有限公司金属精密分公司（抽查检查信息）
    # tag_list = ['1402','1459391','12'] # 昆山中海工贸有限公司（股权出质）
    tag_list = ['1022', '62625187', '15', '91320200060222553', '320200400037279'] # 丸悦（无锡）商贸有限公司(行政处罚)
    # tag_list = ['1022', '1034004', '14', '91320282628411980H', '320282000077425', 'ecipplatform'] # 江苏省伟宇塑业有限公司（动产抵押登记信息（抵押物概况））
    main(id_tag=tag_list)
    print "finished..."



