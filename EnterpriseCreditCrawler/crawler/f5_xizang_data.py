# -*- coding:utf-8 -*-

__author__ = 'lijb'

import os
import re
import requests
from bs4 import BeautifulSoup

# 创建requests请求会话
Session = requests.Session()

# 声明结果变量
result = {}

# 统一基本信息的key
def judge_keyword(dict_ba, dict_keyword):
    '''
    :dict_ba {'A2':'d','B2':'dd','C1':'dw9'}
    :dict_keyword {'A':['A1','A2','A3','A4'],'B':['B1','B2'],'C':['C1']}
    :return: 统一key后的dict
    '''
    for keyword in dict_keyword.keys():
        for prob_keyword in dict_keyword[keyword]:
            if dict_ba.has_key(prob_keyword):
                dict_ba[keyword] = dict_ba.pop(prob_keyword)

    return dict_ba

# 返回页面或版块的soup对象
def get_html(url, *para):
    '''
    :url: url
    :para: 如果不传，返回(),所有元素组成元组
    :return: 返回页面的html的soup对象
    '''
    headers_info = {
        'Host': 'gsxt.xzaic.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
    }
    if para[0]!={}:
        data = para[0]
        req = None
        t = 0
        while t < 10:
            try:
                req = Session.post(url, timeout=20, headers=headers_info, data=data)
                break
            except:
                t += 1
                print u'网络请求失败，第', t + 1, u'次尝试重连……'
    else:
        req = None
        t = 0
        while t < 10:
            try:
                req = Session.post(url, timeout=20, headers=headers_info)
                break
            except:
                t += 1
                print u'网络请求失败，第', t + 1, u'次尝试重连……'
    if req == None:
        print u'多次尝试网络请求失败，请检查网络，然后重启程序。'
        os._exit(0)
    content = req.text
    # print content
    if len(content)<=150:# 这里可以再完善
        return None
    soup = BeautifulSoup(content, 'lxml')

    return soup

# 获取基本信息
def get_dict(pageSoup, *br_keyword, **d):
    '''
    该函数基本上只对基本信息、动产抵押详情的头两个管用
    :param pageSoup: 首页的soup对象
    :param br_keyword: 版块的关键字，可能是中文，也可能是soup对象中tag_name的值
    :param d: soup对象的class值，传递方式如class_='detailsList'
    :return: 以字典形式返回所需信息
    '''

    try:
        info = pageSoup.findAll('table', class_=d["class_"])
        names = data = []
        for i in range(len(br_keyword)):
            for x in info:
                if x.find(text=br_keyword[i]) != None:
                    names = x.find_all('th')
                    data = x.find_all('td')
                    break
        if names == data == []:
            return {}
    except:
        # print("Error: does not have this part.")
        return {}
    names_list = []
    data_list = []
    for name in names[1:]:
        names_list.append(name.text.strip())
    for d in data:
        data_list.append(d.text.strip().replace('\r\n', ''))
    if len(data_list) == 0:
        return {}
    dict_ba = dict(zip(names_list, data_list))

    return dict_ba

# 获取版块信息
def get_dict_list(pageSoup, key_list, *br_keyword):
    '''

    :param pageSoup: 只含有版块soup对象或含有版块的soup对象（需传递br_keyword参数）
    :param key_list: 版块键列表
    :param br_keyword: id 标签名，若没有，下面的代码部分需改成其他，以获取对应的soup对象
    :return: [{},{},{}]
    '''
    # *keyword_tuple: for names and data. a tuple like this : ([]).
    try:
        if br_keyword[0]==[""]:
            data = pageSoup.findAll('td')
        else:
            info = pageSoup.find(id = br_keyword[0])
            data = info.findAll('td')
    except:
        # print("Error: does not have this part.")
        return []
    data_list = []
    for d in data:
        data_list.append(d.text.strip().replace('\r\n', ''))
        # print d.text.strip().replace('\r\n', '')
    if len(data_list) == 0:
        return []
    dict_ba_list = []
    number = len(key_list)
    while data_list!=[]:
        dict_ba = dict(zip(key_list, data_list[0:number]))
        dict_ba_list.append(dict_ba)
        data_list = data_list[number:]

    return dict_ba_list

# ————————————黄————金————分————割————线————子类————————

def mul_page(pageSoup, page_tag, url_page_part, key_list, dlink, idname, glb_id):
    '''
    该函数对分页版块有效，包括详情页里面的分页
    :param pageSoup:
    :param page_tag: 遇到翻页时，页码对应的标签的值，如id='page_tag'
    :param url_page_part: 分页版块的中间部分的url
    :param key_list: 表头
    :param dlink: 对于详情页，这是onclick部分或者href部分
    :param idname: 翻页时对应id所对应的名称
    :param idname: id
    :return: 无返回值
    '''
    dict_ba_list = []
    url_home = "http://gsxt.xzaic.gov.cn/"
    id = glb_id.split("=")[-1]
    if dlink != "":
        a = re.findall("[0-9]+", dlink)
        if a != []:
            id = a[0]
    pagelt = 2 # 声明
    for i in range(2, 100):
        page_i_tag = pageSoup.find(id=(page_tag + str(i)))
        if page_i_tag == None:
            pagelt = i  # max j is i-1.
            break
    br_keyword = [""]
    for j in range(1, pagelt):
        url = url_home + url_page_part
        if idname != "":
            data = {'pno': str(j), idname: id}
        else:
            data = {'pno': str(j), 'mainId': id}
        pageSoup = get_html(url, data)
        if pageSoup != None:
            # print "page:", j
            dict_ba_list_0 = get_dict_list(pageSoup, key_list, br_keyword)
            dict_ba_list = dict_ba_list + dict_ba_list_0

    return dict_ba_list


def detailPage(pageSoup_A, glb_id):
    url_home = "http://gsxt.xzaic.gov.cn/"
    detailTagValue = "mortDiv"
    mulpageTagValue = "spanmort"
    dlinkList = []
    try:
        # info = pageSoup_A.find(id = "mortDiv")#动产抵押登记信息的详情
        info = pageSoup_A.find('div', id=detailTagValue)
        dlinkList = info.findAll('a')
        pagelt = 2
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

        execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
        tableListC = ['dispatcher_qyxx_c_mortgage', 'dispatcher_qyxx_s_creditor', 'dispatcher_qyxx_mortgage']

        pool_d = Pool_d(glb_id)
        for i in range(len(execute_d)):
            print "—" * 20, execute_d[i], "—" * 20
            for d in dlinkList:
                dlink = d['onclick']
                url = url_home + dlink.split("'")[1]
                print url
                pageSoup_d = get_html(url, {})
                if pageSoup_d != None:
                    # print getattr(pool_d, execute_d[i])(dlink, pageSoup_d)
                    result[tableListC[i]] = getattr(pool_d, execute_d[i])(pageSoup_A)

# ————————————黄————金————分————割————线—————————————————————

# 获取数据的大类
class Pool():
    '''
    该类是获取所需信息的主类，实例化时不传递任何参数，参数用在方法中。
    '''
    def __init__(self, glb_id):

        self.glb_id = glb_id

    # QYXX_BASICINFO登记信息（基本信息）
    def basicinfo_execute(self, pageSoup):
        '''
        获取基本信息并插入数据库
        :param pageSoup: 含有所需版块的soup对象
        :return:
        '''
        br_keyword = [u"基本信息"]
        dict_ba = get_dict(pageSoup, br_keyword, class_="detailsList")

        dict_keyword = dict(reg_num=[u'注册号', u'注册号/统一社会信用代码'], company_name=[u'名称', u'公司名称'],
                            owner=[u'法定代表人', u'负责人', u'股东', u'经营者', u'执行事务合伙人', u'投资人'],
                            address=[u'营业场所', u'经营场所', u'住所', u'住所/经营场所'], start_date=[u'成立日期', u'注册日期'],
                            check_date=[u'核准日期', u'发照日期'], fund_cap=[u'注册资本'],
                            company_type=[u'类型'], business_area=[u'经营范围'], business_from=[u'经营期限自', u'营业期限自'],
                            check_type=[u'登记状态', u'经营状态'],
                            authority=[u'登记机关'], locate=[u'区域'])

        dict_ba[u'区域'] = u'西藏'
        dict_ba = judge_keyword(dict_ba, dict_keyword)
        dict_ba_list = []
        dict_ba_list.append(dict_ba)
        return dict_ba_list

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, pageSoup):
        # br_keyword = [u"invDiv"]
        # page_soup = pageSoup.find(id='invDiv')
        page_tag = "spaninv"
        url_page_part = "QueryInvList.jspx?"
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'xiangqing']
        # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型', '详情']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, pageSoup):
        # br_keyword = ["altDiv"]
        # page_soup = pageSoup.find(id='altDiv')
        page_tag = "spanalt"
        url_page_part = "QueryAltList.jspx?"
        key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, pageSoup):
        # br_keyword = ["memDiv"]
        # page_soup = pageSoup.find(id='memDiv')
        page_tag = "spanmem"
        url_page_part = "QueryMemList.jspx?"
        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, pageSoup):
        # br_keyword = ["childDiv"]
        # page_soup = pageSoup.find(id='invDiv')
        page_tag = "spanchild"
        url_page_part = "QueryChildList.jspx?"
        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, pageSoup):
        # br_keyword = ["dongchandiya"]
        # page_soup = pageSoup.find(id='invDiv')
        page_tag = "spanmort"
        url_page_part = "QueryMortList.jspx?"
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority', 'amount', 'status', 'gongshiriqi', 'detail']
        # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'公示日期'	'详情']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, pageSoup):
        # br_keyword = ["guquanchuzhi"]
        # page_soup = pageSoup.find(id='invDiv')
        page_tag = "spanpledge"
        url_page_part = "QueryPledgeList.jspx?"
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'gongshiriqi', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '公示日期', '变化情况']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, pageSoup):
        # br_keyword = ["punDiv"]
        # page_soup = pageSoup.find(id='invDiv')
        page_tag = "spanpun"
        url_page_part = "QueryPunList.jspx?"
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority', 'pun_date', 'gongshiriqi', 'xiangqing']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','公示日期','详情']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, pageSoup):
        # br_keyword = ["excDiv"]
        # page_soup = pageSoup.find(id='invDiv')
        page_tag = "spanexc"
        url_page_part = "QueryExcList.jspx?"
        key_list = ['xuhao', 'reason', 'date_occurred', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '移出异常原因', '移出日期', '作出决定机关']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, "", "",self.glb_id)

        return dict_ba_list

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, pageSoup):
        number = 6
        key_list = ['xuhao', 'reason_in', 'date_in','reason_out','date_out','authority']
        # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']
        br_keyword = ["yanzhongweifaqiye"]
        dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)

        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")

        return dict_ba_list

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, pageSoup):
        number = 5
        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date', 'spot_result']
        # key_list = ['序号','检查实施机关','类型','日期','结果']
        br_keyword = ["chouchaxinxi"]
        dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)

        return dict_ba_list

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, pageSoup):
        number = 7
        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number', 'status', 'xiangqing']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']
        br_keyword = ["EquityFreezeDiv"]
        dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")

        return dict_ba_list

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, pageSoup):
        number = 6
        key_list = ['xuhao','person','stock','person_get','court','xiangqing']
        # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']
        br_keyword = ["xzcfDiv"]
        dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)
        if dict_ba_list != []:
            raise ValueError("dict_ba_list is not empty.")

        return dict_ba_list

# 动产抵押详情
class Pool_d():

    def __init__(self, glb_id):

        self.glb_id = glb_id

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, dlink, pageSoup):
        br_keyword = [u"动产抵押登记信息"]
        dict_ba = get_dict(pageSoup, br_keyword, class_="detailsList")

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return dict_ba

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, dlink, pageSoup):
        br_keyword = [u"被担保债权概况"]
        dict_ba = get_dict(pageSoup, br_keyword, class_='detailsList')

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return dict_ba

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, dlink, pageSoup):
        # br_keyword = ["guaTab"]
        # # page_soup = pageSoup.find(id='guaTab')
        page_tag = "spangua"
        url_page_part = "QueryGuaList.jspx?"
        idname = "mortId"
        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information', 'mortgage_range']
        #     # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']
        dict_ba_list = mul_page(pageSoup, page_tag, url_page_part, key_list, dlink, idname, self.glb_id)

        mortgageInfo = []
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
            mortgageInfo.append(dict_ba)

        return dict_ba_list

def main(id_number):
    # executeX中还没有进行数据库测试的,已经设置了在数据不会空时，raise error。
    # global id
    id = id_number[-32:]
    url_home = "http://gsxt.xzaic.gov.cn/"
    url_part_A = "businessPublicity.jspx?id="
    url = url_home + url_part_A + id
    executeA = ['basicinfo_execute', 's_h_execute', 'b_c_execute',
                'member_execute', 'branch_execute',
                'mortgage_basic_execute', 'pledge_execute', 'adm_punishment_execute', 'abnormal_execute',
                'black_info_execute', 'spot_check_execute']

    tableListA = ['dispatcher_qyxx_basicinfo','dispatcher_qyxx_s_h','dispatcher_qyxx_b_c',
               'dispatcher_qyxx_member','dispatcher_qyxx_branch','dispatcher_qyxx_mortgage_basic',
               'dispatcher_qyxx_pledge','dispatcher_qyxx_adm_punishment','dispatcher_qyxx_abnormal',
               'dispatcher_qyxx_black_info','dispatcher_qyxx_spot_check']

    pool = Pool(id)

    # 工商公示信息
    pageSoup_A = get_html(url, {})
    if pageSoup_A != None:
        for i in range(len(executeA)):
            print "—" * 20, executeA[i], "—" * 20
            # print getattr(pool, executeA[i])(pageSoup_A)
            result[tableListA[i]] = getattr(pool, executeA[i])(pageSoup_A)
            # pool.b_c_execute(pageSoup_A)
    # 司法协助公示信息
    executeB = ['stockholder_change_execute', 'stock_freeze_execute']
    tableListB = ['dispatcher_qyxx_stock_freeze', 'dispatcher_qyxx_stockholder_change']
    url_B = url_home + "justiceAssistance.jspx?id=" + id
    pageSoup_B = get_html(url_B, {})
    if pageSoup_B != None:
        for i in range(len(executeB)):
            print "—" * 20, executeB[i], "—" * 20
            # print getattr(pool, executeB[i])(pageSoup_B)
            result[tableListB[i]] = getattr(pool, executeB[i])(pageSoup_B)

    # 以下是获取动产抵押详情的

    detailPage(pageSoup_A, id)

    print "finished ..."


if __name__ == '__main__':

    id = ['55346621BCEE91DC8EEC2D28C1631870',   # 西藏圣和建筑工程有限公司  变更（翻页）
          '3F645AA1BFAC867D0237AA0909285903',   # 中检集团西藏有限公司 变更信息（更多）
          '7DC9F3E873380171E23BFCDAF07FE7BE',   # 风行不锈钢装饰工程部 经营异常，无股东信息版块，变更有翻页
          'CE1E49085F1317C8DF99D14D8F54C2AA']   # 安多汇鑫矿业有限责任公司 抽查检查        ]

    main(id[1])