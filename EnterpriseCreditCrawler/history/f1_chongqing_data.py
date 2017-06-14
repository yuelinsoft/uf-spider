# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'shanghai'
from __future__ import unicode_literals
from EnterpriseCreditCrawler.common import conf,common
import requests
import json
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
Session = requests.Session()
result = {}

def get_html(url, *para):
    headers_info = {
            'Connection': 'keep-alive',
            'Host': 'gsxt.cqgs.gov.cn',
            # 'Referer': 'http://gsxt.cqgs.gov.cn/search_ent',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
    }
    # if url == "http://gsxt.cqgs.gov.cn/search_getSFXZ.action?":
    #     headers_info['Referer'] = 'http://gsxt.cqgs.gov.cn/search_sfxzgs'
    if para[0]!={}:
        data = para[0]
        req = Session.post(url, timeout=20, headers=headers_info, data=data)
    else:
        req = Session.post(url, timeout=40, headers=headers_info)
    if len(req.text)<=150:# 这里可以再完善
        return None
    a = str(req.text.encode("utf8"))[6:]
    pageSoup = json.loads(a)
    return pageSoup

class Pool():

    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, pageSoup):
        dict_ba = pageSoup["base"]
        dict_ba['区域'] = '重庆市'
        if dict_ba != {}:
            dict_keyword = {
                'company_name': ['entname'],
                'fund_cap': [u'注册资本'],
                'company_type': [u'enttype'],
                'check_type': [u'opstate'],
                'authority': [u'regorg'],
                'check_date': [u'apprdate'],
                'locate': [u'区域'],
                'owner': ['name','pril','lerep'],
                'address': ['oploc', 'dom'],
                'reg_num': ['regno', 'creditcode'],
                'business_area': ['opscoandform','opscope'],
                'start_date': ['estdate'],
                'business_from': ['regdate','opfrom']
            }
            dict_ba = common.judge_keyword(dict_ba, dict_keyword)
            if dict_ba.has_key('regcap'):#备忘
                dict_ba['fund_cap'] = str(dict_ba['regcap']) + '万元人民币'
            dict_ba_list = []
            dict_ba_list.append(dict_ba)
            return dict_ba_list
        else:
            return []

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("qyjy"):
            dict_ba_list = pageSoup["qyjy"]
            dict_keyword = {
                'xuhao':[],
                'reason':['specause'],
                'date_occurred':['publishdate'],
                'juedinglierujiguan':[],
                'reason_out':['remexcpres'],
                'date_out':['remdate'],
                'authority':['decorg']
            }
            if dict_ba_list != []:
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("punishments"):
            dict_ba_list = pageSoup["punishments"]
            if dict_ba_list != []:
                dict_keyword = {
                    'xuhao':[],
                    'pun_number':['pendecno'],
                    'reason':['illegacttype'],
                    'fines':['authcontent'],
                    'authority':['penauth'],
                    'pun_date':['pendecissdate'],
                    'xiangqing':[]
                }
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list


    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("alters"):
            dict_ba_list = pageSoup["alters"]
            dict_keyword = {
                'reason':['altitem'],
                'before_change':['altbe'],
                'after_change':['altaf'],
                'date_to_change':['altdate']
            }
            if dict_ba_list != []:
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list


    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("brunchs"):
            dict_ba_list = pageSoup["brunchs"]
            if dict_ba_list != []:
                dict_keyword = {
                    'xuhao':[],
                    'company_num':['regno','creditcode'],
                    'company_name':['brname'],
                    'authority':['regorgname']
                }
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("members"):
            dict_ba_list = pageSoup["members"]
            dict_keyword = {
                'xuhao':[],
                'person_name':['name'],
                'p_position':['position']
            }
            if dict_ba_list != []:
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list


    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("motage"):
            dict_ba_list = pageSoup["motage"]
            dict_keyword = {
                'xuhao':[],
                'mortgage_reg_num':['morregcno'],
                'date_reg':['regidate'],
                'authority':['regorg'],
                'amount':['priclasecam'],
                'status':['type'],
                'detail':[]
            }
            if dict_ba_list != []:
                for dict_ba in dict_ba_list:
                    if dict_ba.has_key('priclasecam') and dict_ba.has_key('regcapcur'):
                        dict_ba['priclasecam'] = str(dict_ba['priclasecam']) + u'万' + dict_ba['regcapcur']
                    if dict_ba['type']==None or dict_ba['type']=="1":
                        dict_ba['type'] = "有效"
                    if dict_ba['type']=="2":
                        dict_ba['type'] = "无效"
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list


    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("stock"):
            dict_ba_list = pageSoup["stock"]
            if dict_ba_list != []:
                dict_keyword = {
                    'xuhao':[],
                    'reg_code':['equityno'],
                    'pleder':['pledgor'],
                    'id_card':['cerno','blicno'],
                    'plede_amount':['impam'],
                    'brower':['imporg'],
                    'brower_id_card':['impcerno','impno'],
                    'reg_date':['equpledate'],
                    'status':['type'],
                    'changes':[]
                }
                for dict_ba in dict_ba_list:
                    dict_ba['changes'] = ''
                    if dict_ba.has_key('impam') and dict_ba.has_key('pledamunit'):
                        dict_ba['impam'] = str(dict_ba['impam']) + dict_ba['pledamunit']
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("investors"):
            dict_ba_list = pageSoup["investors"]
            if dict_ba_list != []:
                dict_keyword = {
                    's_h_name':['inv'],
                    's_h_id_type':['certype','blictype'],
                    's_h_id':['cerno','blicno'],
                    's_h_type':['invtype']
                }
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("ccjc"):
            dict_ba_list = pageSoup["ccjc"]
            if dict_ba_list != []:
                dict_keyword = {
                    'xuhao':[],
                    'authority':['insauth'],
                    'spot_type':['instype'],
                    'spot_date':['insdate'],
                    'spot_result':['insresname']
                }
                for dict_ba in dict_ba_list:
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list


    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, pageSoup):
        dict_ba_list = []
        dict_ba_list = pageSoup
        if dict_ba_list != []:
            for dict_ba in dict_ba_list:
                if dict_ba.has_key('froam') and dict_ba.has_key('regcapcur'):
                    dict_ba['froam'] = str(dict_ba['froam']) + u'万' + dict_ba['regcapcur']

                    dict_keyword = {
                        'xuhao':[],
                        'person':['inv'],
                        'stock':['froam'],
                        'court':['froauth'],
                        'notice_number':['executeno'],
                        'status':['frozstate'],
                        'xiangqing':[]
                    }
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)

        return dict_ba_list


    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, pageSoup):
        dict_ba_list = pageSoup
        return dict_ba_list

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, pageSoup):
        dict_ba_list = []
        if pageSoup.has_key("illegals"):
            dict_ba_list = pageSoup["illegals"]
            if dict_ba_list != []:
                raise ValueError("dict_ba_list is not empty.")

        return dict_ba_list

class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        dict_ba_list_0 = []
        if pageSoup.has_key("motage"):
            dict_ba_list_0 = pageSoup["motage"]
            if dict_ba_list_0 != []:
                for dict_ba in dict_ba_list_0:
                    dict_ba["pefperformto"] = u'自'+str(dict_ba["pefperform"])+u'至'+str(dict_ba["pefperto"])
                    dict_keyword = {
                        'mortgage_reg_num': ['morregcno'],
                        'date_reg': ['regidate'],
                        'authority': ['regorg'],
                        'mortgage_type': ['priclaseckind'],
                        'amount': ['priclasecam'],
                        'time_range': ['pefperformto'],
                        'mortgage_range': ['warcov']
                    }
                    dict_ba = common.judge_keyword(dict_ba, dict_keyword)
                    # dict_ba = common.c_mortgage_dict(dict_ba)

        return dict_ba_list_0


    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        dict_ba_list_1 = []
        if pageSoup.has_key("motage"):
            dict_ba_list_0 = pageSoup["motage"]
            dict_ba_list_1 = []
            if dict_ba_list_0 != []:
                for dict_ba_0 in dict_ba_list_0:
                    dict_ba_list = dict_ba_0["obligees"]
                    if dict_ba_list != []:
                        for dict_ba in dict_ba_list:
                            dict_ba['priclasecam'] = str(dict_ba['priclasecam']) + u'万元'
                            dict_ba["pefperformto"] = u'自'+str(dict_ba["pefperform"])+u'至'+str(dict_ba["pefperto"])
                            dict_keyword = {
                                'mortgage_type': ['priclaseckind'],
                                'amount': ['priclasecam'],
                                'mortgage_range': ['warcov'],
                                'time_range': ['pefperformto']
                            }
                            dict_ba = common.judge_keyword(dict_ba, dict_keyword)
                            # dict_ba = common.s_creditor_dict(dict_ba)
                            mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0]['mortgage_reg_num']
                            dict_ba['mortgage_reg_num'] = mortgage_reg_num
                            dict_ba_list_1.append(dict_ba)

        return dict_ba_list_1

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):
        dict_ba_list_1 = []
        if pageSoup.has_key("motage"):
            dict_ba_list_0 = pageSoup["motage"]
            if dict_ba_list_0 != []:
                dict_ba_list_1 = []
                for dict_ba_0 in dict_ba_list_0:
                    dict_ba_list = dict_ba_0["pawns"]
                    for dict_ba in dict_ba_list:
                        dict_keyword = {
                            'xuhao':[],
                            'mortgage_name':['guaname'],
                            'belongs':['own'],
                            'information':['guades'],
                            'mortgage_range':['remark']
                        }
                        dict_ba = common.judge_keyword(dict_ba, dict_keyword)
                        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0]['mortgage_reg_num']
                        dict_ba['mortgage_reg_num'] = mortgage_reg_num
                        dict_ba_list_1.append(dict_ba)

        return dict_ba_list_1

def main(**kwargs):
    tag_list = kwargs.get('id_tag')
    global _proxies
    _proxies = kwargs.get('proxies')
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时raise error;raise error先运行。
    executeA = [
            'black_info_execute', 'basicinfo_execute', 'mortgage_basic_execute', 'abnormal_execute',
            'adm_punishment_execute', 'b_c_execute', 'branch_execute', 'member_execute',
            'pledge_execute', 's_h_execute', 'spot_check_execute'
            ]
    executeB = [
        'stock_freeze_execute', 'stockholder_change_execute'
    ]
    execute_d = ['c_mortgage_execute', 's_creditor_execute','mortgage_execute']
    pool = Pool()
    data = {
        'entId': tag_list[0],
        'id': tag_list[1],
        'name': tag_list[2],
        'type': tag_list[3],
    }

    # 司法股东变更登记信息
    url_C = "http://gsxt.cqgs.gov.cn/search_getSFXZGDBG.action?"
    data['stype'] = 'enterprise'
    pageSoup_C = get_html(url_C, data)
    if pageSoup_C != None:
        raise ValueError("dict_ba_list is not empty.")

    # 工商公示信息
    url_A = "http://gsxt.cqgs.gov.cn/search_getEnt.action?"
    data['stype']='SAIC'
    pageSoup_A = get_html(url_A, data)
    if pageSoup_A != None:
        for c in executeA:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] =  getattr(pool, c)(pageSoup_A)
            # common.for_print(result_A)

    # 司法股权冻结信息
    url_B = "http://gsxt.cqgs.gov.cn/search_getSFXZ.action?"
    data['stype']='enterprise'
    pageSoup_B = get_html(url_B, data)
    if pageSoup_B != None:
        for c in executeB:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] =  getattr(pool, c)(pageSoup_B)
            # common.for_print(result_B)

    # 以下是获取详情html的
    pool_d = Pool_d()
    if pageSoup_A != None:
        for c in execute_d:
            print "%r %r %r" % ("*" * 20, c, "*" * 20)
            result[conf.tableDict[c]] = getattr(pool_d, c)(pageSoup_A)
            # common.for_print(result_D)

    return result


if __name__ == '__main__':
    # tag_list=[u'5009051201409010680726', u'500905305254307',u'\u6df1\u5733\u524d\u6d77\u878d\u91d1\u6240\u57fa\u91d1\u7ba1\u7406\u6709\u9650\u516c\u53f8\u91cd\u5e86\u5206\u516c\u53f8',u'2130']#'深圳前海融金所基金管理有限公司重庆分公司'
    # tag_list=[u'5000001201405210547623', u'500103000851800', u'\u91cd\u5e86\u60e0\u6c11\u91d1\u878d\u670d\u52a1\u6709\u9650\u8d23\u4efb\u516c\u53f8', u'1140']#'重庆惠民金融服务有限责任公司'
    # tag_list=[u'500108010100016788', u'500108000110628', u'\u91cd\u5e86\u597d\u58eb\u901a\u623f\u5730\u4ea7\u7ecf\u7eaa\u6709\u9650\u516c\u53f8', u'1130']#'重庆好士通房地产经纪有限公司'
    # tag_list=[u'5002341201504070946773', u'500234007935599', u'\u91cd\u5e86\u6843\u82b1\u6e90\u5c71\u6cc9\u6c34\u6709\u9650\u516c\u53f8', u'1130']#'重庆桃花源山泉水有限公司'
    # tag_list=[u'500902010100004834', u'500902000006177', u'\u91cd\u5e86\u5b66\u5e9c\u533b\u9662\u6295\u8d44\u7ba1\u7406\u6709\u9650\u516c\u53f8', u'1130']#'重庆学府医院投资管理有限公司'
    # tag_list=[u'500903030100000075', u'500000400005327', u'\u91cd\u5e86\u9f99\u6e56\u4f01\u4e1a\u62d3\u5c55\u6709\u9650\u516c\u53f8', u'1001']#'重庆龙湖企业拓展有限公司'
    # tag_list=[u'500228010100005673', u'500228000009792', u'\u6881\u5e73\u53bf\u54c1\u4e4b\u5c71\u519c\u7267\u79d1\u6280\u6709\u9650\u516c\u53f8', u'1130']#'梁平县品之山农牧科技有限公司'
    # tag_list=[u'5003840000122933', u'500384600256650', u'\u5357\u5ddd\u533a\u65f6\u5c1a\u901a\u8baf\u95e8\u5e02\u90e8', u'9999']#'南川区时尚通讯门市部'
    tag_list=[u'500237010100004493', u'500237000010054', u'\u91cd\u5e86\u5eb7\u78a7\u7279\u98df\u54c1\u6709\u9650\u516c\u53f8', u'1130']#'重庆康碧特食品有限公司'
    # tag_list=[u'500225010100001054', u'500225300003593', u'\u91cd\u5e86\u5e02\u5927\u8db3\u804c\u4e1a\u6280\u672f\u6559\u80b2\u540e\u52e4\u670d\u52a1\u4e2d\u5fc3', u'4320']#'重庆市大足职业技术教育后勤服务中心'
    # tag_list=[u'5001060000009530', u'500106300018858', u'\u91cd\u5e86\u5de5\u7a0b\u804c\u4e1a\u6280\u672f\u5b66\u9662\u62db\u5f85\u6240', u'4310']#'重庆工程职业技术学院招待所'
    main(id_tag=tag_list)




