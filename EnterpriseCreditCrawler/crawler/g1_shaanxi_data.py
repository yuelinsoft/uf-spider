# -*- coding:utf-8 -*-
'''与四川共用训练集，代码也一致，除了一些有关url的参数不一样外。'''
__author__ = 'lijb'

import os
from bs4 import BeautifulSoup
import requests
import time

Session = requests.Session()

# 声明结果变量
result = {}

# 返回页面或版块的soup对象
def get_html(url, *para):
    '''
    :url: url
    :para: 如果不传，返回(),所有元素组成元组
    :return: 返回页面的html的soup对象
    '''
    headers_info = {
            'Host': 'xygs.snaic.gov.cn',
            'Origin': 'http://xygs.snaic.gov.cn',
            'Referer': 'http://xygs.snaic.gov.cn/ztxy.do',
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
    :param br_keyword: 版块的关键字
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

        if names == data == []: return {}
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
    该函数返回除基本信息以外的其他信息
    :param pageSoup: 只含有版块soup对象或含有版块的soup对象（需传递br_keyword参数）
    :param key_list: 字段名key
    :param br_keyword: id 标签名，若没有，下面的代码部分需改成其他，以获取对应的soup对象
    :return: [{},{},{}]
    '''
    try:
        if br_keyword[0] == "":
            data = pageSoup.find_all('td')
        else:
            info = pageSoup.find(id = br_keyword[0])
            data = info.find_all('td')
    except:
        # print("Error: does not have this part.")
        return []
    data_list = []
    for d in data:
        try:
            span = d.find_all('span')[1]   # 判断是否存在更多的点击项，去第二个span标签，beforeMore*
            data_list.append(span.text.replace(u'收起更多', '').strip().replace('\r\n', ''))
        except:
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

# 动产抵押详情
def detailPage(pagesoup, id):
    '''
    该函数获取动产抵押详情页面信息并爬取其中三块内容。
    :param pagesoup: 动产抵押登记信息版块的soup对象
    :return:
    '''
    # 带详情的tr标签
    tr = pagesoup.find_all('tr', {'name': 'dc'})
    a = []
    for each in tr:
        td = each.find_all('td')
        # 找第8个 td 标签下的 a 标签
        a.append(td[7].find('a'))
    onclick = []
    if a != []:
    # 进入if，说明存在动产抵押基本信息
        for each in a:
        # 循环 a 标签，获取 onclick
            try:
                click = each['onclick'].split("'")[1]
            except:
                # 有动产抵押登记信息，但是没有详情页面的链接
                break
            onclick.append(click)
        # 循环结束得到的结果是onclick里面的类似于id 的 有效数字字符串的集合
    if onclick != []:
    # 进入if，说明有详情页面。下面就根据onclick里的数字id字符串获取详情页的具体信息
        url = 'http://gsxt.scaic.gov.cn/ztxy.do'
        for click in onclick:
            data = {
                'method': 'dcdyDetail',
                'maent.pripid': id,
                'maent.xh': click,
                'random': str(int(time.time() * 1000))
            }
            # 单个动产抵押详情的soup对象，可用该对象实例化pool_d类
            soup = get_html(url, data)
            pool = Pool_d()
            execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
            tableListC = ['dispatcher_qyxx_c_mortgage', 'dispatcher_qyxx_s_creditor', 'dispatcher_qyxx_mortgage']
            for i in range(len(execute_d)):
                print '*' * 20, execute_d[i], '*' * 20
                # print getattr(pool, exe)(soup)
                result[tableListC[i]] = getattr(pool, execute_d[i])(soup)

# 动产抵押详情
class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, dlink, pageSoup):
        br_keyword = u"动产抵押登记信息"
        dict_ba = get_dict(pageSoup, br_keyword, class_="detailsList")

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return dict_ba

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, dlink, pageSoup):
        br_keyword = u"被担保债权概况"
        dict_ba = get_dict(pageSoup, br_keyword, class_='detailsList')

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return dict_ba

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, dlink, pageSoup):
        br_keyword = "table_dywgk"
        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information', 'mortgage_range']
        # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']
        dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)

        mortgageInfo = []
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
            mortgageInfo.append(dict_ba)

        return dict_ba_list  # 抵押物概况，字典列表

# 公示信息
class Pool():

    def __init__(self, id):
        '''
        :param id: 企业首页url中的id
        '''
        self.id = id
        self.url = 'http://xygs.snaic.gov.cn/ztxy.do'
        self.headers = {
                'Host':'xygs.snaic.gov.cn',
                'Origin':'http://xygs.snaic.gov.cn',
                'Referer': 'http://xygs.snaic.gov.cn/ztxy.do',
                'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
            }

    # ******登记信息******
    def dengjiSoup(self):
        '''
        :return: 登记信息版块的soup对象
        '''
        data = {
            'method': 'qyInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk1',
            'random': str(int(time.time() * 1000))
        }

        soup = get_html(self.url, data)

        return soup

    # 基本信息
    def basicinfo_execute(self):
        '''
        :return: 基本信息 dict
        '''
        # 调用dengjiSoup函数返回soup对象
        soup = self.dengjiSoup()
        Info_list = []
        if soup != None:
            tbody = soup.find('div', {'id': 'jibenxinxi'})
            # jbxx = tbody.find('table', {'class': 'detailsList'})  # jbxx：基本信息

            # 调用外部get_dict函数
            br_keyword = [u'基本信息 ']
            Info = get_dict(tbody, br_keyword[0], class_='detailsList')

            dict_keyword = dict(reg_num=[u'注册号', u'注册号/统一社会信用代码'], company_name=[u'名称', u'公司名称'],
                                owner=[u'法定代表人', u'负责人', u'股东', u'经营者', u'执行事务合伙人', u'投资人'],
                                address=[u'营业场所', u'经营场所', u'住所', u'住所/经营场所'], start_date=[u'成立日期', u'注册日期'],
                                check_date=[u'核准日期', u'发照日期'], fund_cap=[u'注册资本'],
                                company_type=[u'类型'], business_area=[u'经营范围'], business_from=[u'经营期限自', u'营业期限自'],
                                check_type=[u'登记状态', u'经营状态'],
                                authority=[u'登记机关'], locate=[u'区域'])

            Info[u'区域'] = u'陕西省'
            Info = judge_keyword(Info, dict_keyword)

            Info_list.append(Info)

        return Info_list

    # 股东信息
    def s_h_execute(self):
        '''
        :return: 股东信息 list
        '''
        # 调用dengjiSoup函数返回soup对象
        soup = self.dengjiSoup()

        info_soup = soup.find('table', {'id': 'table_fr'})

        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'detail']
        # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型', '详情']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # 变更信息
    def b_c_execute(self):
        '''
        :return: 变更信息 list,其顺序为 [u'变更事项',u'变更前内容',u'变更后内容',u'变更日期']
        '''
        # 调用dengjiSoup函数返回soup对象
        soup = self.dengjiSoup()

        info_soup = soup.find('table', {'id': 'table_bg'})

        key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        info = get_dict_list(info_soup, key_list,'')
        # 对于存在‘更多’的，需要添加后处理操作

        return info # 字典列表

    # *****备案信息******
    def beianSoup(self):
        '''
        :return: 返回备案信息页面的soup对象
        '''
        data = {
            'method': 'baInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk2',
            'random': str(int(time.time() * 1000))
        }

        soup = get_html(self.url, data)

        return soup

    # 主要成员信息
    def member_execute(self):
        '''
        :return: 主要成员信息 list, 是 [姓名，职位] 列表
        '''
        # 调用beianSoup函数，获取soup
        soup = self.beianSoup()

        info_soup = soup.find('table', {'id': 'table_ry1'})

        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # 分支机构信息
    def branch_execute(self):
        '''
        :return: 分支机构信息
        '''
        # 调用beianSoup函数，获取soup
        soup = self.beianSoup()

        info_soup = soup.find('table', {'id': 'table_fr2'})

        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # ******动产抵押登记******
    def mortgage_basic_execute(self):
        '''
        :return: 动产抵押登记信息
        '''
        data = {
            'method': 'dcdyInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk4',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_dc'})

        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority', 'amount', 'status', 'gongshiriqi', 'detail']
        # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'公示日期'	'详情']
        info = get_dict_list(info_soup, key_list, '')

        if info != []:
            raise ValueError("dict_ba_list is not empty.")

        return info  # 字典列表

    # ******股权出资登记信息******
    def pledge_execute(self):
        '''
        :return: 股权出资登记信息
        '''
        data = {
            'method': 'gqczxxInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk4',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_gq'})

        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'gongshiriqi', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '公示日期', '变化情况']
        info = get_dict_list(info_soup, key_list, '')

        if info != []:
            raise ValueError("dict_ba_list is not empty.")

        return info  # 字典列表

    # ******行政处罚信息******
    def adm_punishment_execute(self):
        '''
        :return: 行政处罚信息
        '''
        data = {
            'method': 'cfInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk3',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_gscfxx'})

        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority', 'pun_date', 'gongshiriqi', 'detail']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','公示日期','详情']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # ******经营异常信息******
    def abnormal_execute(self):
        '''
        :return: 经营异常信息
        '''
        data = {
            'method': 'jyycInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk6',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_yc'})

        key_list = ['xuhao', 'reason', 'date_occurred', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '移出异常原因', '移出日期', '作出决定机关']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # ******严重违法信息******
    def black_info_execute(self):
        '''
        :return: 严重违法信息
        '''
        data = {
            'method': 'yzwfInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk14',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_wfxx'})

        key_list = ['xuhao', 'reason_in', 'date_in', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # ******抽查检查信息******
    def spot_check_execute(self):
        '''
        :return: 抽查检查信息
        '''
        data = {
            'method': 'ccjcInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk7',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_ccjc'})

        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date', 'spot_result']
        # key_list = ['序号','检查实施机关','类型','日期','结果']
        info = get_dict_list(info_soup, key_list, '')

        return info  # 字典列表

    # ******股权冻结信息******
    def stock_freeze_execute(self):
        '''
        :return: 司法股权冻结信息
        '''
        data = {
            'method': 'sfgsInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk17',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_gqdj'})

        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number', 'status', 'detail']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']
        info = get_dict_list(info_soup, key_list, '')

        if info != []:
            raise ValueError("dict_ba_list is not empty.")

        return info  # 字典列表

    # ******股东变更信息******
    def stockholder_change_execute(self):
        '''
        :return: 司法股东变更登记信息
        '''
        data = {
            'method': 'sfgsbgInfo',
            'maent.pripid': self.id,
            'czmk': 'czmk18',
            'random': str(int(time.time() * 1000))
        }

        # 调用外部get_soup函数
        soup = get_html(self.url, data)

        info_soup = soup.find('table', {'id': 'table_gdbg'})

        key_list = ['xuhao', 'person', 'stock', 'person_get', 'court', 'detail']
        # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']
        info = get_dict_list(info_soup, key_list, '')

        if info != []:
            raise ValueError("dict_ba_list is not empty.")

        return info  # 字典列表

def main(id):
    executeA = ['pledge_execute', 'mortgage_basic_execute',
                'basicinfo_execute', 's_h_execute', 'b_c_execute',
                'member_execute', 'branch_execute',
                'adm_punishment_execute', 'abnormal_execute',
                'black_info_execute', 'spot_check_execute']
    tableListA = ['dispatcher_qyxx_pledge', 'dispatcher_qyxx_mortgage_basic',
                  'dispatcher_qyxx_basicinfo', 'dispatcher_qyxx_s_h', 'dispatcher_qyxx_b_c',
                  'dispatcher_qyxx_member', 'dispatcher_qyxx_branch',
                  'dispatcher_qyxx_adm_punishment', 'dispatcher_qyxx_abnormal',
                  'dispatcher_qyxx_black_info', 'dispatcher_qyxx_spot_check']

    executeB = ['stock_freeze_execute', 'stockholder_change_execute']
    tableListB = ['dispatcher_qyxx_stock_freeze', 'dispatcher_qyxx_stockholder_change']

    pool = Pool(id)
    # 工商公示
    for i in range(len(executeA)):
        print "*" * 20, executeA[i], "*" * 20
        # print getattr(pool, each_get)()  # 依次执行Pool里面的各个函数
        result[tableListA[i]] = getattr(pool, executeA[i])()

    # 司法协助
    for i in range(len(executeB)):
        print "*" * 20, executeB[i], "*" * 20
        # print getattr(pool, each_get)()  # 依次执行Pool里面的各个函数
        result[tableListB[i]] = getattr(pool, executeB[i])()
        # pool.b_c_execute()
        # print x

    # 以下是获取动产抵押详情html的（不一定有）
    data = {
        'method': 'dcdyInfo',
        'maent.pripid': id,
        'czmk': 'czmk4',
        'random': str(int(time.time() * 1000))
    }

    # 调用外部get_soup函数
    url = 'http://xygs.snaic.gov.cn/ztxy.do'
    pageSoup_A = get_html(url, data)
    detailPage(pageSoup_A, id)
    print "finished ..."


if __name__ == '__main__':

    id = ['6100002078140', # 陕西景鑫商贸有限公司(严重违法，变更（翻页），行政处罚，经营异常)
          '6105253000006567', # 澄城县牵手婚庆营业部(抽查检查)
          '6100002022353',
          '8610526000008042']# 蒲城县朝阳街宁春土产日杂经销部  变更信息

    main(id[0])