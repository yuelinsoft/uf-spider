# -*- coding: utf-8 -*-
# author: 'KEXH'
# source: 'guizhou'
from common import conf,common
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
Session = requests.Session()
result = {}

# 获取字段网址：
# http://gsxt.gzgs.gov.cn/2016/nzgs/jbxx.jsp?k=f951c25425f384470604189df08ed35cf88edc803f93cc0819780e253130777b

def get_html(url, *para):
    # info = []
    headers_info = {
                    'Host': 'gsxt.gzgs.gov.cn',
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:44.0) Gecko/20100101 Firefox/44.0'
                    }
    if para[0]!={}:
        data = para[0]
    # print url,data
    req = Session.get(url, timeout=20, headers=headers_info, params=data)
    info = req.content
    # jsonA = json.loads(req.content)
    # if jsonA.has_key("data"):
    #     info = jsonA["data"]
    # else:
    #     info = jsonA
    return info

def insertCursor(table,fields,val,data):
    '''
    table = "QYXX_BASICINFO"
    fields = "(ID, DATE_INPUT)"
    val = "QYXX_DETAIL_ID.nextval,:区域,trunc(sysdate)"
    data = (i.get('',''),i.get('区域',''))
    insertCursor(table,fields,val,data)
    '''
    sql = "INSERT INTO " + table + fields + "VALUES (" + val +")"
    cursor.execute(sql, data)
    conn.commit()

def detailPage(list_, execute_d):
    url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
    data = {
        'pageIndex': '0',
        'pageSize': '25'
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
                # common.for_print(result_D)

class Pool():
    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '5'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info == []:
            url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchOldData.shtml"
            data = {
                'pageIndex': '1',
                'pageSize': '1'
            }
            data['nbxh'] = list_[0]
            info = get_html(url, data)
        if info != []:
            for i in info:
                i = common.basicinfo_dict(i,u'江西')
        dict_ba_list = info
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '33'
        }
        data['nbxh'] = list_[0]
        dict_ba_list = get_html(url, data)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '38'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info == []:
            url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchOldData.shtml"
            info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '3'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '9'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        # url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '8'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        if info == []:
            url = "http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchData.shtml"
            data['pageIndex'] = '1'
            data['pageSize'] = '3'
            info = get_html(url, data)
        if info != []:
            for i in info:
                dict_keyword = {
                                'xm': ['jyzm']
                                }
                i = common.judge_keyword(i, dict_keyword)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '25'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '4'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '2',
            'pageSize': '3'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '35'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息###000
    def stock_freeze_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '557'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###000
    def stockholder_change_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '557'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return None

    # QYXX_BLACK_INFO严重违法信息###000
    def black_info_execute(self, list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '557'
        }
        data['nbxh'] = list_[0]
        info = get_html(url, data)
        dict_ba_list = info
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
            'pageIndex': '0',
            'pageSize': '26'
        }
        data['dcnbxh'] = list_i
        info = get_html(url, data)
        dict_ba_list = info
        return dict_ba_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, list_i):
        url = "http://gsxt.gzgs.gov.cn/2016/frame/query!searchDcdy.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '28'
        }
        data['dcnbxh'] = list_i
        info = get_html(url, data)
        dict_ba_list = info
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(list_i)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, list_i):
        url = "http://gsxt.gzgs.gov.cn/2016/frame/query!searchDcdy.shtml"
        data = {
            'pageIndex': '0',
            'pageSize': '29'
        }
        data['dcnbxh'] = list_i
        info = get_html(url, data)
        dict_ba_list = info
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(list_i)[0]['mortgage_reg_num']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
        return dict_ba_list

def main(id_list):
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时raise error;raise error先运行。
    # 'black_info_execute', 'stock_freeze_execute', 'stockholder_change_execute'
    print 1
    tag_list = id_list[0]
    # '''
    # 基本信息：
    # urllist = ["http://gsxt.jxaic.gov.cn/baseinfo/queryenterpriseinfoByRegnore.do"]
    # datalist = [{}]
    # '''
    # '''
    # 股东信息：
    # urllist = ["http://gsxt.jxaic.gov.cn/einvperson/getqueryeInvPersonService.do"]
    # datalist = [{'pageIndex': '0', 'pageSize': '5'}]
    # '''
    # '''
    # 变更信息：
    # urllist = ["http://gsxt.jxaic.gov.cn/gtalterrecoder/getquerygtalterrecoder.do?"]
    # datalist = [{'pageIndex': '0', 'pageSize': '5'}]
    # '''
    # '''
    # '''
    # urllist = [
    #     "http://gsxt.jxaic.gov.cn/ebrchinfo/getqueryEBrchinfo.do?","http://gsxt.jxaic.gov.cn/opadetail/getqueryopdetail.do?","http://gsxt.jxaic.gov.cn/opadetail/queryTotalPage.do?",
    #     "http://gsxt.jxaic.gov.cn/eliqmbr/getqueryeliqmbr.do?","http://gsxt.jxaic.gov.cn/epriperson/queryPerson.do?","http://gsxt.jxaic.gov.cn/ebrchinfo/queryTotalPage.do?",
    #     "http://gsxt.jxaic.gov.cn/gtalterrecoder/queryTotalPage.do?","http://gsxt.jxaic.gov.cn/stateinfopages/fgsqyfrxx/.do?","http://gsxt.jxaic.gov.cn/opadetail/getqueryopdetail/.do?"
    #     ]
    # datalist = [{},{'pageIndex': '0','pageSize': '5'}]#,{'pageIndex': '0','pageSize': '23'},{'pageIndex': '0','pageSize': '55'},{'pageIndex': '0','pageSize': '60'},{'pageIndex': '0','pageSize': '58'},
    # #     {'pageIndex': '0','pageSize': '18'},{'pageIndex': '0','pageSize': '15'},{'pageIndex': '0','pageSize': '20'},{'pageIndex': '0','pageSize': '21'},{'pageIndex': '0','pageSize': '22'},{'pageIndex': '0','pageSize': '24'}]
    #
    # for url in urllist:
    #     for data in datalist:
    #         data['pripid'] = tag_list
    #         info = get_html(url, data)
    #         if len(info)>20:
    #             print "*"*20
    #             print info
    #             print url
    #             print data
    #             time.sleep(3)
    #         # if info != []:
    #         #     for i in info:
    #         #         for d in i: print d, i[d]
    #         #     raise ValueError("[info] is not empty. Please copy these for check:",(data,url))

    execute = ['basicinfo_execute'#, 'adm_punishment_execute', 'spot_check_execute', 'b_c_execute', 'branch_execute',
               # 'pledge_execute', 'abnormal_execute', 'member_execute', 's_h_execute', 'mortgage_basic_execute'
               ]
    # execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
    pool = Pool()
    for c in execute:
        print "%r %r %r" % ("*" * 20, c, "*" * 20)
        result[conf.tableDict[c]] = getattr(pool, c)(tag_list)
        # common.for_print(result_A)
    #
    # # 以下是获取详情html的
    # detailPage(tag_list, execute_d)

if __name__ == "__main__":
    # tag_list = "MzYxMTI3MjAxNDEwMDkwMDMxNTQ2MAu002Cu002C"
    # tag_list = "MzYwMDAwMjAwMDAwMDMzMAu002Cu002C"
    # main(tag_list)
    Tlist = [
        ['MzYwNzMyMjAxMzAzMTkwMDA2MzA4MQ=', 'MzYwNzMyMzEwMDA2Mjk', 'MzYwNzMyMzEwMDA2Mjk'],  # 兴国县鑫龙机砖厂
        ['MzYyMTIxMDA3MDkyMDA1MDUzMDAwMTE', 'MzYwNzIxNjAwMDIwOTI', 'MzYwNzIxNjAwMDIwOTI'],  # 赣县三鑫金银加工店
        ['MzYwNzI2MjAxNDExMTQwMDM2MzgwOQ=', 'MzYwNzI2MjEwMDA0NzE', 'MzYwNzI2MjEwMDA0NzE'],  # 赣州市奇峰园林绿化工程有限公司
        ['MzYwNzAyMjAxNTA1MTkwMDE2MzMzMw=', 'MzYwNzAyMjEwMDgwNTA', 'MzYwNzAyMjEwMDgwNTA'],  # 赣州市宇涵汽车贸易有限公司
        ['MzYwNzAyMDA2MjAxNDExMTQwMDM2NDM5MA=', 'MzYwNzAyNjAwNDU3NzQ', 'MzYwNzAyNjAwNDU3NzQ'],  # 章贡区怡美广告设计中心
        ['MzYwNzgyMjAxMzA1MTYwMDE0MTQwNg=', 'MzYwNzgyMjEwMDE3MzA', 'MzYwNzgyMjEwMDE3MzA'],  # 赣州市红土地园林工程有限公司
        ['MzYwNzMyMDA3MjAwOTExMDkzMDAwNA=', 'MzYwNzMyNjAwMTUxNTM', 'MzYwNzMyNjAwMTUxNTM'],  # 兴国县好美佳装饰材料商行
        ['MzYwNzAzMDA1MjAxNTAxMjMwMDAyNzc3Mg=', 'MzYwNzAzNjAwMTMzMTI', 'MzYwNzAzNjAwMTMzMTI'],  # 赣州经济技术开发区潭东镇赖忠国烟花爆竹经销部
        ['MzYwNzgyMDExMjAxNDA1MzAwMDE2NjI2Nw=', 'MzYwNzgyNjAwMzYwODM', 'MzYwNzgyNjAwMzYwODM'],  # 南康区华俊万佳超市
        ['MzYyMTIzMDAxMDEyMDA2MDYyOTAwMDI', 'MzYwNzIyMTEwMDAwMDM', 'MzYwNzIyMTEwMDAwMDM'],  # 国网江西信丰县供电有限责任公司
        ['MzYyMTMzMDAxMDkyMDA2MDUxMjAwMTU', 'MzYwNzMyNjAwMDM2NjU', 'MzYwNzMyNjAwMDM2NjU'],  # 兴国县家盛副食商行
        ['MzYwNzMxMDAyMjAxMjA5MjQwMDI4OTYyNw=', 'MzYwNzMxNjAwMjEzMjI', 'MzYwNzMxNjAwMjEzMjI'],  # 于都焦点视觉婚纱摄影店
        ['MzYwNzgxMDEzMjAwOTA1MjczMDAwNg=', 'MzYwNzgxNjAwMDcyMTI', 'MzYwNzgxNjAwMDcyMTI'],  # 瑞金市象湖镇金乐福超市
        ['MzYwNzgxMDA4MjAxNDEwMDkwMDMxNTE4Mw=', 'MzYwNzgxNjAwMjA5ODQ', 'MzYwNzgxNjAwMjA5ODQ'],  # 瑞金市象湖镇德佳旺香烛店
        ['MzYwNzIxMDA3MjAwOTEwMjIzMDAwMw=', 'MzYwNzIxNjAwMTA0OTA', 'MzYwNzIxNjAwMTA0OTA'],  # 赣县中学北校区
        ['MzYwNzAzMDA2MjAxNTAyMDQwMDAzODg2NA=', 'MzYwNzAzNjAwMTM0MDM', 'MzYwNzAzNjAwMTM0MDM'],  # 赣州开发区嘉和石材加工厂
        ['MzYwNzMxMDAyMjAxMDEwMTMzMDAxNQ=', 'MzYwNzMxNjAwMTIwNDY', 'MzYwNzMxNjAwMTIwNDY'],  # 于都县光明封箱胶纸厂
        ['MzYwNzAyMjAxNDA2MTgwMDE4OTc2MQ=', 'MzYwNzAyNjAwNDMzNDQ', 'MzYwNzAyNjAwNDMzNDQ'],  # 章贡区锦尚酒业经营部
        ['MzYwNzAwMjAwNzA4MTYwMDAwMDA3OTE', 'MzYwNzAwMTEwMDAwNDQ', 'MzYwNzAwMTEwMDAwNDQ'],  # 赣州江钨新型合金材料有限公司
        ['MzYwNzgyMDA1MjAxMzA0MTcwMDEwMjk2MA=', 'MzYwNzgyNjAwMzA3Mjc', 'MzYwNzgyNjAwMzA3Mjc'],  # 南康区华兴玻璃厂
        ['MzYwNzAyMjAxNDExMjQwMDM3NTA5Ng=', 'MzYwNzAyMjEwMDcyMDg', 'MzYwNzAyMjEwMDcyMDg'],  # 赣州创鑫服装有限公司
        ['MjAxNjAzMTUxMTQ3MjA2OTg4ODM', 'MzYwNzI2NjEwMDAzODE', 'MzYwNzI2NjEwMDAzODE'],  # 安远县天心镇南坑小学
        ['MzYwNzIzMjAxNTA1MTUwMDE1NjUwNw=', 'MzYwNzIzNjAwMTgxNzY', 'MzYwNzIzNjAwMTgxNzY'],  # 大余县润发农副产品经销部
        ['MzYwNzAzMjAxNDExMTcwMDM2NTMxNw=', 'MzYwNzAzMjEwMDE5NDg', 'MzYwNzAzMjEwMDE5NDg'],  # 赣州市钜玮贸易有限公司
        ['MzYyMTIyMDAxMDEyMDA2MDEwNTAwMDE', 'MzYwNzgyMTIwMDAwMDU', 'MzYwNzgyMTIwMDAwMDU'],  # 赣州银行股份有限公司南康支行
        ['MzYwNzIzMDA2MjAxMzAxMDkwMDAwNTg5Nw=', 'MzYwNzIzNjAwMTQ2NTg', 'MzYwNzIzNjAwMTQ2NTg'],  # 大余县新时代智能手机城
        ['MzYwNzAyMDAyMjAxMDExMDgwMDAxNzE3Ng=', 'MzYwNzAyNjAwMjIzOTE', 'MzYwNzAyNjAwMjIzOTE'],  # 章贡区瑞通电器经营部
        ['MzYwNzAyMDAyMjAxNTA0MjAwMDExNDIzMQ=', 'MzYwNzAyNjAwNDk0MTk', 'MzYwNzAyNjAwNDk0MTk'],  # 章贡区双龙副食商行
        ['MzYwNzI0MjAxMjAzMDkwMDA0ODg0MA=', 'MzYwNzI0MjEwMDA0Njk', 'MzYwNzI0MjEwMDA0Njk'],  # 江西宏辉旅游开发有限责任公司
        ['MzYwNzAwMjAwODAzMDMwMDAwMDI3NTQ', 'MzYwNzAwMjEwMDAzNTI', 'MzYwNzAwMjEwMDAzNTI'],  # 赣州市天龙电器有限公司
        ['MzYwNzI2MDA1MjAxMjA5MjgwMDI5NTA4OQ=', 'MzYwNzI2NjAwMTE3Mzg', 'MzYwNzI2NjAwMTE3Mzg'],  # 安远县浮槎乡利源塑料颗粒厂
        ['MzYwNzAyMDAzMjAxMDA3MjIzMDAwMw=', 'MzYwNzAyNjAwMjAxNzA', 'MzYwNzAyNjAwMjAxNzA'],  # 章贡区元华银玉缘首饰店
        ['MzYwNzAyMDA5MjAxNDA1MjAwMDE1MTc0Mg=', 'MzYwNzAyNjAwNDU2MTA', 'MzYwNzAyNjAwNDU2MTA'],  # 章贡区腾飞餐馆
        ['MzYwNzAyMDAzMjAwOTA3MDgzMDAwMw=', 'MzYwNzAyNjAwMTMzNzg', 'MzYwNzAyNjAwMTMzNzg'],  # 章贡区吉田饰品商行
        ['MzYwNzMzMDA0MjAxMDA4MjczMDAwMw=', 'MzYwNzMzNjAwMDc0NzM', 'MzYwNzMzNjAwMDc0NzM'],  # 会昌县昌鸿商行
        ['MzYwNzAyMjAxNDEwMjIwMDMzNDMwNA=', 'MzYwNzAyMjEwMDcxMDE', 'MzYwNzAyMjEwMDcxMDE'],  # 赣州金美兰环保科技有限公司
        ['MzYwNzMyMDA3MjAxMjA1MTAwMDEzMTU4OQ=', 'MzYwNzMyNjAwMjMwNDc', 'MzYwNzMyNjAwMjMwNDc'],  # 兴国县华轩灯具商行
        ['MzYwNzI3MDAyMjAxMjA5MjQwMDI4OTA4NQ=', 'MzYwNzI3NjAwMTQzMDQ', 'MzYwNzI3NjAwMTQzMDQ'],  # 龙南县庆豪商务宾馆
        ['MzYwNzIyMDA3MjAxNDA1MTYwMDE0NzU1Nw=', 'MzYwNzIyNjAwMjc0MTk', 'MzYwNzIyNjAwMjc0MTk'],  # 信丰县军军商行
        ['MzYwNzI1MDA1MjAxNDAzMDUwMDA0MTk1MA=', 'MzYwNzI1NjAwMTI1NzY', 'MzYwNzI1NjAwMTI1NzY'],  # 崇义县汇源副食商行
        ['MzYwNzMwMjAxNTAzMjMwMDA3MjYwNw=', 'MzYwNzMwMjEwMDEyMTI', 'MzYwNzMwMjEwMDEyMTI'],  # 赣州宁之源生物质颗粒有限公司
        ['MzYwNzI0MjAxMTA4MjkwMDI2NDEyNg=', 'MzYwNzI0MjEwMDAzOTQ', 'MzYwNzI0MjEwMDAzOTQ'],  # 赣州富强商贸有限公司
        ['MzYwNzAwMjAxMjAzMjAwMDA2MzE2Mg=', 'MzYwNzAwMjEwMDM3NzQ', 'MzYwNzAwMjEwMDM3NzQ'],  # 赣州天狐纸业有限公司
        ['MzYyMTAyMDAyMDIyMDA2MDUzMDA0Mjg', 'MzYwNzAyNjAwMTg3ODg', 'MzYwNzAyNjAwMTg3ODg'],  # 赣州市章贡区阿里山茶庄
        ['MzYwNzgyMDExMjAxMTA0MTkwMDEwNjI0NA=', 'MzYwNzgyNjAwMjA2Mzc', 'MzYwNzgyNjAwMjA2Mzc'],  # 南康区金丽嘉化纤棉制品厂
        ['MzYwNzAyMDAyMjAwOTEwMTQzMDAwNg=', 'MzYwNzAyNjAwMTQ4NTY', 'MzYwNzAyNjAwMTQ4NTY'],  # 章贡区蓉蓉日用品商行
        ['MzYwNzAyMjAxNDAxMjEwMDAxNzg3MA=', 'MzYwNzAyMjEwMDU3MjY', 'MzYwNzAyMjEwMDU3MjY'],  # 赣州杜兰商贸有限公司
        ['MzYyMTI0MDA2MDEyMDA1MDIyODAxMjg', 'MzYwNzIzMTIwMDAwMzM', 'MzYwNzIzMTIwMDAwMzM'],  # 中国太平洋财产保险股份有限公司赣州中心支公司
        ['MzYwNzgyMDEyMjAwODA4MTkzMDAwMw=', 'MzYwNzgyNjAwMDQ4Nzg', 'MzYwNzgyNjAwMDQ4Nzg'],  # 潭口兴业针织厂
        ['MzYwNzgyMjAxNDA0MDIwMDA4Nzg0Mg=', 'MzYwNzgyMjEwMDIzMTk', 'MzYwNzgyMjEwMDIzMTk'],  # 江西汇康装饰工程有限公司
        ['MzYwNzAzMjAxMjEwMjQwMDMxODI5OA=', 'MzYwNzAzMjEwMDA5NTA', 'MzYwNzAzMjEwMDA5NTA'],  # 赣州建大农林发展有限公司
        ['MzYwNzAyMjAxNTExMjAwMDQwMDc3OA=', 'MzYwNzAyMjEwMDg5MDM', 'MzYwNzAyMjEwMDg5MDM'],  # 赣州盛誉装饰有限公司
        ['MzYwNzgyMDExMjAxNTA0MDkwMDA5Njg4Mw=', 'MzYwNzgyNjAwNDAxMjE', 'MzYwNzgyNjAwNDAxMjE'],  # 南康区鹏古铝合金制品加工部
        ['MzYwNzI2MjAxNDExMTQwMDM2MzgwOQ=', 'MzYwNzI2MjEwMDA0NzE', 'MzYwNzI2MjEwMDA0NzE'],  # 赣州市奇峰园林绿化工程有限公司
        ['MzYwNzMyMjAxMjA0MTIwMDA5NjEyOQ=', 'MzYwNzMyMjEwMDA2MzU', 'MzYwNzMyMjEwMDA2MzU'],  # 兴国银创家居装饰有限公司
        ['MzYwNzMwMjAxMzAxMjIwMDAxODczNA=', 'MzYwNzMwMjEwMDA2ODA', 'MzYwNzMwMjEwMDA2ODA'],  # 宁都县明强电子产品有限公司
        ['MzYwNzAyMDA5MjAxNDA1MjAwMDE1MTc0Mg=', 'MzYwNzAyNjAwNDU2MTA', 'MzYwNzAyNjAwNDU2MTA'],  # 章贡区腾飞餐馆
        ['MzYwNzI1MDA3MjAxMTAzMjgwMDA3MzUwMA=', 'MzYwNzI1NjAwMDg2MjQ', 'MzYwNzI1NjAwMDg2MjQ'],  # 崇义县丰州乡毛利竹制品厂
        ['MzYwNzAyMjAxMzEwMDgwMDI4MzcwMw=', 'MzYwNzAyMjEwMDU5MjE', 'MzYwNzAyMjEwMDU5MjE'],  # 赣州非常柒加壹装饰工程有限公司
        ['MzYwNzIzMjAxNDA0MTkwMDExMDM5OQ=', 'MzYwNzIzMjEwMDA2ODU', 'MzYwNzIzMjEwMDA2ODU'],  # 大余县嘉和商贸有限责任公司
        ['MzYwNzgyMjAxNDA5MDIwMDI3ODM1MA=', 'MzYwNzgyMzIwMDAwNTg', 'MzYwNzgyMzIwMDAwNTg'],  # 赣州市南康区华亨气站
    ]

    for tag_list in Tlist:
        print tag_list[2]
        main(tag_list)
        # print "*******"
        # time.sleep(5)
