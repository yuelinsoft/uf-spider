#coding=utf-8
from EnterpriseCreditCrawler.common import conf, common, url_requests
import requests
import json
import traceback
from EnterpriseCreditCrawler.common.page_parse import CreditInfo
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
result={}

def get_html(url,*args):
    #args接受的 是元组
    info=[]
    headers={
        'Host': 'gsxt.gzgs.gov.cn',
        'Referer': 'http://gsxt.gzgs.gov.cn/2016/xq.jsp',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'
    }
    if args[0] !={}:
        data=args[0]
        response=url_requests.post(url=url,data=data,headers=headers,cookies=cookies,proxies=proxies,timeout=60)
    else:
        response=url_requests.post(url=url,headers=headers,cookies=cookies,proxies=proxies,timeout=60)
    jsonA=json.loads(response.content)
    if jsonA.has_key("data"):
        info=jsonA["data"]
    return info

#如果基本信息里面有动产抵押的信息就执行这个函数获取动产抵押详情页面里的数据
def detailPage(list_,execute_d):
    url='http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml'
    data={
        'c':'0',
        't':'25'
    }
    data['nbxh']=list_
    info=get_html(url,data)
    if info ==[]:
        url='http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml'
        info=get_html(url,data)
    if info !=[]:
        mortgage_detail=[]
        result['qyxx_c_mortgage'] = []
        result['qyxx_s_creditor'] = []
        result['qyxx_mortgage'] = []
        tagDetail_list=[]
        for i in info:
            #根据dcnbxh来发送请求
            tagDetail_list.append(i['dcnbxh'])
        for list_i in tagDetail_list:
            pool_d=Pool_d()

            for i in range(len(execute_d)):
                print "%r %r %r" % ("*" * 20, execute_d[i], "*" * 20)
                if i==0:
                    for li in  getattr(pool_d,execute_d[i])(list_i):
                        result['qyxx_c_mortgage'].append(li)
                if i==1:
                    for li in getattr(pool_d,execute_d[i])(list_i):
                        result['qyxx_s_creditor'].append(li)
                if i==2:
                    for li in getattr(pool_d,execute_d[i])(list_i):
                        result['qyxx_mortgage'].append(li)

    else:
        result['qyxx_c_mortgage']=[]
        result['qyxx_s_creditor']=[]
        result['qyxx_mortgage']=[]

class Pool():

    def __init__(self):
        pass

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self,list_):
        url='http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml'
        data={
            'c':'0',
            't':'5'
        }
        data["nbxh"]=list_
        info=get_html(url,data)
        if info==[]:
            url='http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml'
            data={
                'c':'1',
                't':'1'
            }
            data["nbxh"]=list_
            info=get_html(url,data)
        if info !=[]:
            for i in info:
                i["区域"]=u'贵州'
                dict_keyword = {
                                'qymc': ['***','zhmc'],#
                                'fddbr': ['jyzm'],#经营者
                                'qylxmc': ['zcxsmc'],#组成形式
                                'yyrq1':  ['jyqsrq']#核准日期
                                }
                i=common.judge_keyword(i,dict_keyword)

                #如果没有 这个键变换参数再发请求
                if i.has_key("mclxmc")==False:
                    url_1="http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
                    data_1={
                        'c':'0',
                        't':'57'
                    }
                    data_1['nbxh']=list_
                    info_1=get_html(url_1,data_1)
                    if info_1[0].has_key('mclxmc'):
                        i['mclxmc']=info_1[0]['mclxmc']

            dict_ba_list=info
            dict_keyword = {
                'company_name': ['qymc'],  # 公司名称
                'check_type': ['mclxmc'],  # 续存
                'fund_cap': ['zczb'],  # 注册资本  #如果没有注册资本怎么办？
                'company_type': ['qylxmc'],  # 组织形式
                'authority': ['djjgmc'],  # 机关
                'check_date': ['hzrq'],  # 核准日期
                'locate': ['区域'],
                'owner': ['fddbr'],#经营者
                'address': ['zs'],#地址
                'reg_num': ['zch'],  # 注册号
                'business_area': ['jyfw'],  # 经营范围
                'start_date': ['clrq'], #注册日期
                'business_from': ['yyrq1']  # 营业期限自
            }
            dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
            for li in dict_ba_list:
                if li.has_key("fund_cap")==False:
                    li["fund_cap"]=None
            return dict_ba_list
        else:
            return None

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self,list_):
        url='http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml'
        data={
            'c':'2',
            't':'3'
        }
        data['nbxh']=list_
        dict_ba_list=get_html(url,data)
        dict_keyword={
            'xuhao':[],
            's_h_type': ['tzrlxmc'],
            's_h_name': ['czmc'],
            's_h_id_type': ['zzlxmc'],
            's_h_id': ['zzbh']
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self,list_):
        url='http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml'
        data={
            'c':'0',
            't':'3'
        }
        data['nbxh']=list_
        dict_ba_list=get_html(url,data)
        dict_keyword={
            'xuhao':[],
            'reason': ['bcsxmc'],#变更事项
            'date_to_changes': ['hzrq'],#变更日期
            'before_changes': ['bcnr'],#变更前
            'after_changes': ['bghnr']#变更后
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml"
        data={
            'c':'0',
            't':'8'
        }
        data["nbxh"]=list_
        info=get_html(url,data)
        if info==[]:
            url="http://gsxt.gzgs.gov.cn/2016/gtgsh/query!searchData.shtml"
            data['c']=1
            data['t']=3
            info=get_html(url,data)
        if info !=[]:
            for i in info:
                dict_keyword = {
                                'xm': ['jyzm']
                                }
                i=common.judge_keyword(i,dict_keyword)
        dict_ba_list=info
        dict_keyword={
            'xuhao':[],
            'person_name': ['xm'],
            'p_position': ['zwmc']
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml"
        data={
            'c':"0",
            't':'9'
        }
        data["nbxh"]=list_
        dict_ba_list=get_html(url,data)
        dict_keyword={
            'xuhao':[],
            'company_num': ['fgszch'],
            'company_name': ['fgsmc'],
            'authority': ['fgsdjjgmc']
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data={
            'c':0,
            't':25
        }
        data["nbxh"]=list_
        dict_ba_list=get_html(url,data)
        dict_keyword={
            'xuhao':[],
            'mortgage_reg_num': ['djbh'],
            'date_reg': ['djrq'],
            'authority': ['djjgmc'],
            'amount': ['bdbse'],
            'status': ['zt'],
            'gongshiriqi':[],
            'detail': []
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list


    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self,list_):
        url = "http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data={
            'c':'0',
            't':'4'
        }
        data["nbxh"]=list_
        dict_ba_list=get_html(url,data)
        dict_keyword={
            'xuhao':[],
            'reg_code': ['djbh'],
            'pleder': ['czr'],
            'id_card': ['czzjhm'],
            'plede_amount': ['czgqse'],
            'brower': ['zqr'],
            'brower_id_card': ['zqzjhm'],
            'reg_date': ['czrq'],
            'staues': ['zt'],
            'changes': []  # 变更
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self,list_):
        url="http://gz.gsxt.gov.cn/2016/nzgs/query!searchOldData.shtml"
        data={
            'c':'0',
            't':'38'
        }
        data["nbxh"]=list_
        try:
            info=get_html(url,data)
        except:
            info=[{'wfxwlx':u'由于网络原因请求数据失败，请稍后再尝试查询'}]
        if info==[]:
            url="http://gz.gsxt.gov.cn/2016/nzgs/query!searchOldData.shtml"
            try:
                info=get_html(url,data)
            except:
                info = [{'wfxwlx':u'由于网络原因请求数据失败，请稍后再尝试查询'}]
        dict_ba_list=info
        dict_keyword = {
            'xuhao':[],
            'pun_number': ['cfjdsh'],
            'reason': ['wfxwlx'],
            'fines': ['xzcfnr'],
            'authirty': ['cfjg'],
            'pun_date': ['cfrq'],
            'xiangqing':[]
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self,list_):
        # http://gz.gsxt.gov.cn/2016/nzgs/query!searchData.shtml
        url="http://gz.gsxt.gov.cn/2016/nzgs/query!searchData.shtml"
        data={
            'c':"0",
            't':'33'
        }
        data["nbxh"]=list_
        dict_ba_list=get_html(url,data)

        dict_keyword = {
            'xuhao':[],
            'reason': ['lryy'],
            'date_occurred': ['lrrq'],
            'reason_out': ['ycyy'],
            'juedinglierujiguan': [''],
            'date_out': ['ycrq'],
            'authority': ['ycjg']
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data={
            'c':"0",
            "t":"557"
        }
        data["nbxh"]=list_[0]
        dict_ba_list=get_html(url,data)
        if dict_ba_list!=[]:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data={
            'c':"0",
            't':'35'
        }
        data["nbxh"]=list_
        dict_ba_list=get_html(url,data)
        dict_keyword = {
            'xuhao':[],
            'authority': ['ssjg'],#机关
            'spot_type': ['cclx'],#类型
            'spot_date': ['ccrq'],#日期
            'spot_result': ['ccjg']#结果
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/query!searchData.shtml"
        data={
            'c':'0',
            't':'557'
        }
        data['nbxh']=list_
        dict_ba_list=get_html(url,data)
        if dict_ba_list!=[]:
            raise ValueError("dict_ba_list is not empty.")
        else:
            return dict_ba_list

# QYXX_B_C股权更变信息，写入到B_C表中的！！！需要改写
    def stockholder_change_execute(self,list_):
        url="http://gsxt.gzgs.gov.cn/2016/nzgs/query!searchData.shtml"
        data={
            'c':'0',
            't':'23'
        }
        data["nbxh"]=list_
        info=get_html(url,data)
        dict_ba_list=info
        dict_keyword={
            'xuhao':[],#序号
            'person': ['gd'],#股东
            'stock': ['bgqbl'],#变更前比例
            'person_get': ['bghbl'],#变更后比例
            'court': ['bgrq'],#股权变更日期
            'detail':[],#公示日期
        }
        dict_ba_list=common.judge_keyword_1(dict_ba_list,dict_keyword)
        return dict_ba_list

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
            'mortgage_reg_num': ['djbh'],#登记编号
            'date_reg': ['djrq'],
            'authority': ['djjgmc'],#机关
            'mortgage_type': ['bdbzl'],#种类
            'amount': ['bdbse'],#数额
            'time_range': ['qx'],#期限
            'mortgage_range': ['dbfw']#担保范围
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
            'mortgage_type': ['bdbzl'],#种类
            'amount': ['bdbse'],#数额
            'mortgage_range': ['dbfw'],#担保范围
            'time_range': ['qx']#期限
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
            'xuhao':[],
            'mortgage_name': ['mc'],#名称
            'belongs': ['syq'],#所有权归属
            'information': ['xq'],#数量
            'mortgage_range': ['bz']#备注
        }
        dict_ba_list = common.judge_keyword_1(dict_ba_list, dict_keyword)
        return dict_ba_list

def main(**kwargs):
    tag_list=kwargs.get('id_tag')[0]
    global cookies
    cookies=kwargs.get('id_tag')[1]
    global proxies
    proxies = kwargs.get('proxies')
    execute=['basicinfo_execute', 's_h_execute','b_c_execute','member_execute','branch_execute',
             'mortgage_basic_execute',
             'pledge_execute',
             'adm_punishment_execute',
             'abnormal_execute',
             'black_info_execute',
             'spot_check_execute',
             'stock_freeze_execute',
             'stockholder_change_execute',
               ]

    #获取动产抵押登记详情页面需要执行的函数
    execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
    pool=Pool()
    for c in execute:
        print "%r %r %r" % ("*" * 20, c, "*" * 20)
        #result字典的键为表名值为对应函数返回的列表
        result[conf.tableDict[c]]=getattr(pool,c)(tag_list)
        #common.for_print(result[conf.tableDict[c]])

    #获取动产抵押详情页面里的数据
    detailPage(tag_list,execute_d)
    return result

if __name__=="__main__":
    tag_list= '79aa3dc46bda3c659b3ab1f94966cebcf88edc803f93cc0819780e253130777b'
    global cookies
    cookies=None
    print main(id_tag=tag_list,cookies=cookies)


#f951c25425f384470604189df08ed35cf88edc803f93cc0819780e253130777b
# main(['f951c25425f384470604189df08ed35cf88edc803f93cc0819780e253130777b'])#贵州金伟莲贸易有限公司：经营异常，股东信息，主要人员
# main(['79aa3dc46bda3c659b3ab1f94966cebcf88edc803f93cc0819780e253130777b'])#经开区杨氏尖椒鸡店：行政处罚
# main(['501b3410a60c6bb5948e0c80a2f39229f88edc803f93cc0819780e253130777b'])#贵州铂安科技有限责任公司：变更信息, 股权出质
#main(['86cb449fd26d78ac6434dd0ee6c83ad1f88edc803f93cc0819780e253130777b'])#贵州文惠物资贸易有限公司：动产抵押
# main(['c301baf5136b660c5312b16414c0cadff88edc803f93cc0819780e253130777b'])#贵州润辉鹏商贸有限公司：抽查检查
# main(['e3c08c3ec16cfe02f3a9916f74a2be98f88edc803f93cc0819780e253130777b'])#贵州创榜建筑装饰工程有限公司：分支机构
# main(['79aa3dc46bda3c659b3ab1f94966cebcf88edc803f93cc0819780e253130777b'])
# main(['b933ec30890bf379fdae7645446fe8c0f88edc803f93cc0819780e253130777b'])
# main(['1a5401d753d4a8249e525bcac83a397af88edc803f93cc0819780e253130777b'])#贵州省新新建筑工程公司
#main['dd368dd670a4bbff28dbcf3d1ef8a648f88edc803f93cc0819780e253130777b']#贵州开磷集团矿肥有限责任公司 股权变更信息

#f951c25425f384470604189df08ed35cf88edc803f93cc0819780e253130777b            贵阳云岩贵华鞋行