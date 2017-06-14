# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'chongqing', 'jiangshu'
from EnterpriseCreditCrawler.common import conf,common
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
Session = requests.Session()
result = {}

'''
获取字段网址：
http://gsxt.gzgs.gov.cn/2016/nzgs/jbxx.jsp?k=f951c25425f384470604189df08ed35cf88edc803f93cc0819780e253130777b
'''

def get_html(url, *para):
    info = []
    headers_info = {
                    'Host': 'gsxt.gzgs.gov.cn',
                    'Referer': 'http://gsxt.gzgs.gov.cn/2016/xq.jsp',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
                    }
    if para[0]!={}:
        data = para[0]
        req = Session.post(url, timeout=20, headers=headers_info, data=data)
    else:
        req = Session.post(url, timeout=40, headers=headers_info)
    jsonA = json.loads(req.content)
    if jsonA.has_key("data"):
        info = jsonA["data"]
    return info

def detailPage(list_, execute_d):
    url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
    data = {
        'c': '0',
        't': '25'
    }
    data['nbxh'] = list_[0]
    info = get_html(url, data)
    if info == []:
        url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchOldData.shtml"
        info = get_html(url, data)
    if info != []:
        tagDetail_list =[]
        for i in info:
            tagDetail_list.append(i['dcnbxh'])
        for list_i in tagDetail_list:
            pool_d = Pool_d()
            for c in execute_d:
                print "%r %r %r" % ("*" * 20, c, "*" * 20)
                result[conf.tableDict[c]] = getattr(pool_d, c)(list_i)
                common.for_print(result[conf.tableDict[c]])

class Pool():
    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '5'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info == []:
            url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchOldData.shtml"
            data = {
                'c': '1',
                't': '1'
            }
            data['nbxh'] = list_[0]
            info = get_html(url, data)
        if info != []:
            for i in info:
                i['区域'] = '贵州'
                dict_keyword = {
                                '***': ['qymc','zhmc'],
                                'fddbr': ['jyzm'],
                                'qylxmc': ['zcxsmc'],
                                'yyrq1':  ['jyqsrq']
                                }
                i = common.judge_keyword(i, dict_keyword)
                if i.has_key('mclxmc')==False:
                    url_1 = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
                    data_1 = {
                            'c': '0',
                            't': '57'
                            }
                    data_1['nbxh'] = list_[0]
                    info_1 = get_html(url_1, data_1)
                    if info_1[0].has_key('mclxmc'):
                        i['mclxmc'] = info_1[0]['mclxmc']
            dict_ba_list = info
            dict_keyword = {
                'company_name': ['qymc'],
                'reg_num': ['zch'],
                'owner': ['fddbr'],
                'address': ['zs'],
                'start_date': ['clrq'],
                'fund_cap': ['zczb'],
                'company_type': ['qylxmc'],
                'business_area': ['jyfw'],
                'check_type': ['mclxmc'],
                'authority': ['djjgmc'],
                'check_date': ['hzrq'],
                'business_from': ['yyrq1'],
                'locate': [u'区域']
            }
            dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
            return dict_ba_list
        else:
            return None

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '33'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'reason': ['lryy'],
            'date_occurred': ['lrrq'],
            'reason_out': ['ycyy'],
            'date_out': ['ycrq'],
            'authority': ['zcjdjg']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '38'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info == []:
            url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchOldData.shtml"
            info = get_html(url, data)
        dict_ba_list = info
        dict_keyword = {
            'pun_number': ['cfjdsh'],
            'reason': ['wfxwlx'],
            'fines': ['xzcfnr'],
            'authirty': ['cfjg'],
            'pun_date': ['cfrq']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '3'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'reason': ['bcsxmc'],
            'date_to_changes': ['hzrq'],
            'before_changes': ['bcnr'],
            'after_changes': ['bghnr']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '9'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'company_num': ['fgszch'],
            'company_name': ['fgsmc'],
            'authority': ['fgsdjjgmc']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        # url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchData.shtml"
        data = {
            'c': '0',
            't': '8'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info == []:
            url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchData.shtml"
            data['c'] = '1'
            data['t'] = '3'
            info = get_html(url, data)
        if info != []:
            for i in info:
                dict_keyword = {
                                'xm': ['jyzm']
                                }
                i = common.judge_keyword(i, dict_keyword)
        dict_ba_list = info
        dict_keyword = {
            'person_name': ['xm'],
            'p_position': ['zwmc']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '25'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'mortgage_reg_num': ['djbh'],
            'date_reg': ['djrq'],
            'authority': ['djjgmc'],
            'amount': ['bdbse'],
            'status': ['zt']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '4'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'reg_code': ['djbh'],
            'pleder': ['czr'],
            'id_card': ['czzjhm'],
            'plede_amount': ['czgqse'],
            'brower': ['zqr'],
            'brower_id_card': ['zqzjhm'],
            'reg_date': ['czrq'],
            'staues': ['zt']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '2',
            't': '3'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            's_h_type': ['tzrlxmc'],
            's_h_name': ['czmc'],
            's_h_id_type': ['zzlxmc'],
            's_h_id': ['zzbh']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '35'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'authority': ['ssjg'],
            'spot_type': ['cclx'],
            'spot_date': ['ccrq'],
            'spot_result': ['ccjg']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息###000
    def stock_freeze_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '557'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_B_C股权更变信息，写入到B_C表中的！！！
    def stockholder_change_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml"
        data = {
            'c': '0',
            't': '23'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info != []:
            for i in info:
                i['gd'] = u"【股权变更】股东："+i['gd']
        dict_ba_list = info
        dict_keyword = {
            'reason': ['gd'],
            'date_to_changes': ['bgrq'],
            'before_changes': ['bgqbl'],
            'after_changes': ['bghbl']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_BLACK_INFO严重违法信息###000
    def black_info_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'c': '0',
            't': '557'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

class Pool_d():
    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, list_i):
        url = "http://gsxt.gzgs.gov.cn/2016/frame/query!searchDcdy.shtml"
        data = {
            'c': '0',
            't': '26'
        }
        data['dcnbxh'] = list_i
        dict_ba_list = get_html(url, data)
        dict_keyword = {
            'mortgage_reg_num': ['djbh'],
            'date_reg': ['djrq'],
            'authority': ['djjgmc'],
            'mortgage_type': ['bdbzl'],
            'amount': ['bdbse'],
            'time_range': ['qx'],
            'mortgage_range': ['dbfw']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, list_i):
        url = "http://gsxt.gzgs.gov.cn/2016/frame/query!searchDcdy.shtml"
        data = {
            'c': '0',
            't': '28'
        }
        data['dcnbxh'] = list_i
        dict_ba_list = get_html(url, data)
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(list_i)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        dict_keyword = {
            'mortgage_type': ['bdbzl'],
            'amount': ['bdbse'],
            'mortgage_range': ['dbfw'],
            'time_range': ['qx']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, list_i):
        url = "http://gsxt.gzgs.gov.cn/2016/frame/query!searchDcdy.shtml"
        data = {
            'c': '0',
            't': '29'
        }
        data['dcnbxh'] = list_i
        dict_ba_list = get_html(url, data)
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(list_i)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        dict_keyword = {
            'mortgage_name': ['mc'],
            'belongs': ['syq'],
            'information': ['xq'],
            'mortgage_range': ['bz']
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

def main(**kwargs):
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时raise error;raise error先运行。
    # 'black_info_execute', 'stock_freeze_execute', 'stockholder_change_execute'

    # urllist = ["http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml","http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchOldData.shtml"]
    # datalist = [{'c': '0','t': '39'},{'c': '0','t': '55'},{'c': '0','t': '60'},{'c': '0','t': '58'},
    #     {'c': '0','t': '18'},{'c': '0','t': '15'},{'c': '0','t': '21'},{'c': '0','t': '22'},{'c': '0','t': '24'}]
    # print "39jfl"
    # for url in urllist:
    #     for data in datalist:
    #         data['nbxh'] = tag_list[0]
    #         info = get_html(url, data)
    #         if info != []:
    #             print 555
    #             for i in info:
    #                 for d in i: print d, i[d]
    #             raise ValueError("[info] is not empty. Please copy these for check:",(data,url))
    tag_list = kwargs['id_tag']
    execute = ['basicinfo_execute', 'stockholder_change_execute', 'adm_punishment_execute', 'spot_check_execute', 'b_c_execute', 'branch_execute',
               'pledge_execute', 'abnormal_execute', 'member_execute', 's_h_execute', 'mortgage_basic_execute']
    execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']

    pool = Pool()
    for c in execute:
        print "%r %r %r" % ("*" * 20, c, "*" * 20)
        result[conf.tableDict[c]] = getattr(pool, c)(tag_list)
        common.for_print(result[conf.tableDict[c]])

    # # 以下是获取详情html的
    detailPage(tag_list, execute_d)
    return result

if __name__ == "__main__":
    # main(['f951c25425f384470604189df08ed35cf88edc803f93cc0819780e253130777b'])#贵州金伟莲贸易有限公司：经营异常，股东信息，主要人员
    # main(['79aa3dc46bda3c659b3ab1f94966cebcf88edc803f93cc0819780e253130777b'])#经开区杨氏尖椒鸡店：行政处罚
    # main(['501b3410a60c6bb5948e0c80a2f39229f88edc803f93cc0819780e253130777b'])#贵州铂安科技有限责任公司：变更信息, 股权出质
    # main(['86cb449fd26d78ac6434dd0ee6c83ad1f88edc803f93cc0819780e253130777b'])#贵州文惠物资贸易有限公司：动产抵押
    # main(['c301baf5136b660c5312b16414c0cadff88edc803f93cc0819780e253130777b'])#贵州润辉鹏商贸有限公司：抽查检查
    # main(['e3c08c3ec16cfe02f3a9916f74a2be98f88edc803f93cc0819780e253130777b'])#贵州创榜建筑装饰工程有限公司：分支机构
    # main(['79aa3dc46bda3c659b3ab1f94966cebcf88edc803f93cc0819780e253130777b'])
    # main(['b933ec30890bf379fdae7645446fe8c0f88edc803f93cc0819780e253130777b'])
    # main(['1a5401d753d4a8249e525bcac83a397af88edc803f93cc0819780e253130777b'])#贵州省新新建筑工程公司

    main(id_tag=['dd368dd670a4bbff28dbcf3d1ef8a648f88edc803f93cc0819780e253130777b'])#
    # Tlist = [
    # ]
    # for tag_list in Tlist:
    #     main(tag_list)
    #     print "*******"
    #     time.sleep(25)

