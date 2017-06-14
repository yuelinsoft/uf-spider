# -*- coding:utf-8 -*-
"""
    四川 date

    @author: lijianbin
"""


from __future__ import unicode_literals

import time
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo

# # 返回页面或版块的soup对象
# def get_html(url, *para):
#     '''
#     :url: url
#     :para: 如果不传，返回(),所有元素组成元组
#     :return: 返回页面的html的soup对象
#     '''
#     headers_info = {
#             'Host': 'gsxt.scaic.gov.cn/',
#             'Origin': 'http://gsxt.scaic.gov.cn/',
#             'Referer': 'http://gsxt.scaic.gov.cn/ztxy.do',
#             'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
#         }
#
#     if para[0]!={}:
#         data = para[0]
#         req = None
#         t = 0
#         while t < 10:
#             try:
#                 req = Session.post(url, timeout=20, headers=headers_info, data=data)
#                 break
#             except:
#                 t += 1
#                 print u'网络请求失败，第', t + 1, u'次尝试重连……'
#     else:
#         req = None
#         t = 0
#         while t < 10:
#             try:
#                 req = Session.post(url, timeout=20, headers=headers_info)
#                 break
#             except:
#                 t += 1
#                 print u'网络请求失败，第', t + 1, u'次尝试重连……'
#     if req == None:
#         print u'多次尝试网络请求失败，请检查网络，然后重启程序。'
#         os._exit(0)
#     content = req.text
#     # print content
#     if len(content)<=150:# 这里可以再完善
#         return None
#     soup = BeautifulSoup(content, 'lxml')
#
#     return soup
#
# # 获取基本信息
# def get_dict(pageSoup, *br_keyword, **d):
#     '''
#     该函数基本上只对基本信息、动产抵押详情的头两个管用
#     :param pageSoup: 首页的soup对象
#     :param br_keyword: 版块的关键字
#     :param d: soup对象的class值，传递方式如class_='detailsList'
#     :return: 以字典形式返回所需信息
#     '''
#     try:
#         info = pageSoup.findAll('table', class_=d["class_"])
#         names = data = []
#         for i in range(len(br_keyword)):
#             for x in info:
#                 p = x.find(text=br_keyword[i])
#                 if x.find(text=br_keyword[i]) != None:
#                     names = x.find_all('th')
#                     data = x.find_all('td')
#                     break
#
#         if names == data == []: return {}
#     except:
#         # print("Error: does not have this part.")
#         return {}
#     names_list = []
#     data_list = []
#     for name in names[1:]:
#         names_list.append(name.text.strip())
#     for d in data:
#         data_list.append(d.text.strip().replace('\r\n', ''))
#     if len(data_list) == 0:
#         return {}
#     dict_ba = dict(zip(names_list, data_list))
#
#     return dict_ba
#
# # 获取版块信息
# def get_dict_list(pageSoup, key_list, *br_keyword):
#     '''
#
#     :param pageSoup: 只含有版块soup对象或含有版块的soup对象（需传递br_keyword参数）
#     :param number: key 的个数
#     :param br_keyword: id 标签名，若没有，下面的代码部分需改成其他，以获取对应的soup对象
#     :return: [{},{},{}]
#     '''
#     try:
#         if br_keyword[0] == "":
#             data = pageSoup.find_all('td')
#         else:
#             info = pageSoup.find(id = br_keyword[0])
#             data = info.find_all('td')
#     except:
#         # print("Error: does not have this part.")
#         return []
#     data_list = []
#     for d in data:
#         try:
#             span = d.find_all('span')[1]   # 判断是否存在更多的点击项，去第二个span标签，beforeMore*
#             data_list.append(span.text.replace(u'收起更多', '').strip().replace('\r\n', ''))
#         except:
#             data_list.append(d.text.strip().replace('\r\n', ''))
#         # print d.text.strip().replace('\r\n', '')
#     if len(data_list) == 0:
#         return []
#     dict_ba_list = []
#     number = len(key_list)
#     while data_list!=[]:
#         dict_ba = dict(zip(key_list,data_list[0:number]))
#         dict_ba_list.append(dict_ba)
#         data_list = data_list[number:]
#
#     return dict_ba_list
#
# def judge_keyword(dict_ba, dict_keyword):
#     '''
#     :dict_ba {'A2':'d','B2':'dd','C1':'dw9'}
#     :dict_keyword {'A':['A1','A2','A3','A4'],'B':['B1','B2'],'C':['C1']}
#     :return: 统一key后的dict
#     '''
#     for keyword in dict_keyword.keys():
#         for prob_keyword in dict_keyword[keyword]:
#             if dict_ba.has_key(prob_keyword):
#                 dict_ba[keyword] = dict_ba.pop(prob_keyword)
#
#     return dict_ba
#
# # ————————————上面五个个函数通用————————————

# 动产抵押详情
# def detailPage(soup, id):
#     '''
#     该函数获取动产抵押详情页面信息并爬取其中三块内容。
#     :param soup: 动产抵押登记信息版块的soup对象
#     :return:
#     '''
#     # 带详情的tr标签
#     tr = soup.find_all('tr', {'name': 'dc'})
#     a = []
#     for each in tr:
#         td = each.find_all('td')
#         # 找第8个 td 标签下的 a 标签
#         a.append(td[7].find('a'))
#     onclick = []
#     if a != []:
#     # 进入if，说明存在动产抵押基本信息
#         for each in a:
#         # 循环 a 标签，获取 onclick
#             try:
#                 click = each['onclick'].split("'")[1]
#             except:
#                 # 有动产抵押登记信息，但是没有详情页面的链接
#                 break
#             onclick.append(click)
#         # 循环结束得到的结果是onclick里面的类似于id 的 有效数字字符串的集合
#     if onclick != []:
#     # 进入if，说明有详情页面。下面就根据onclick里的数字id字符串获取详情页的具体信息
#         url = 'http://gsxt.scaic.gov.cn/ztxy.do'
#         for click in onclick:
#             data = {
#                 'method': 'dcdyDetail',
#                 'maent.pripid': id,
#                 'maent.xh': click,
#                 'random': str(int(time.time() * 1000))
#             }
#             # 单个动产抵押详情的soup对象，可用该对象实例化pool_d类
#             soup = get_html(url, data) # 通过此soup对象，获取动产抵押的登记编号，并作为参数传递到Pool_d 类里面
#
#             pool = Pool_d()
#             execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
#             tableListC = ['dispatcher_qyxx_c_mortgage', 'dispatcher_qyxx_s_creditor', 'dispatcher_qyxx_mortgage']
#             for i in range(len(execute_d)):
#                 print '*' * 20, execute_d[i], '*' * 20
#                 # print getattr(pool, exe)(soup)
#                 result[tableListC[i]] = getattr(pool, execute_d[i])(soup)

# 动产抵押详情
# class Pool_d():
#
#     def __init__(self):
#         pass
#
#     # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
#     def c_mortgage_execute(self, pageSoup, dlink=None):
#         br_keyword = u"动产抵押登记信息"
#         dict_ba = get_dict(pageSoup, br_keyword, class_="detailsList")
#
#         return dict_ba
#
#     # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
#     def s_creditor_execute(self, pageSoup, dlink=None):
#         br_keyword = u"被担保债权概况"
#         dict_ba = get_dict(pageSoup, br_keyword, class_='detailsList')
#         mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
#         dict_ba['mortgage_reg_num'] = mortgage_reg_num
#
#         return dict_ba
#
#     # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
#     def mortgage_execute(self, pageSoup, dlink=None):
#         br_keyword = u"table_dywgk"
#         # number = 5
#         key_list = ['xuhao', 'mortgage_name', 'belongs', 'information', 'mortgage_range']
#         # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']
#         dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)
#         mortgageInfo = []
#         for dict_ba in dict_ba_list:
#             mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
#             dict_ba['mortgage_reg_num'] = mortgage_reg_num
#             mortgageInfo.append(dict_ba)
#
#         return mortgageInfo # 返回抵押物详情

# ————————————————————上面几个函数是专用于动产抵押情况的

# 公示信息
class CompanyInfo(CreditInfo):

    def __init__(self):

        self.url = 'http://gsxt.scaic.gov.cn/ztxy.do'
        self.headers = {
            'Host': 'gsxt.scaic.gov.cn',
            'Origin': 'http://gsxt.scaic.gov.cn',
            'Referer': 'http://gsxt.scaic.gov.cn/ztxy.do',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/52.0.2743.82 Safari/537.36')
        }
        super(CompanyInfo, self).__init__()

    def basicinfo_execute(self, id):
        """基本信息"""

        data = {
            'method': 'qyInfo',
            'maent.pripid': id,
            'czmk': 'czmk1',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            self.reg_soup = soup.find('div', {'id': 'jibenxinxi'})    #
            # 保存登记信息的soup对象，用于股东与变更。

            info = self.parse(pageSoup=self.reg_soup,
                              tag='table',
                              attrs={'class': 'detailsList'})

            if info:
                info[0] = common.basicinfo_dict(info[0], '四川省')

            self.qyxx_basicinfo = info

    # 股东信息
    def s_h_execute(self, id):
        """股东信息"""

        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'detail']
        # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型', '详情']

        self.qyxx_s_h = self.parse(pageSoup=self.reg_soup,
                                   tag='table',
                                   attrs={'id': 'table_fr'},
                                   key_list=key_list)

    # 变更信息
    def b_c_execute(self, id):
        """变更信息 """

        key_list = ['reason', 'before_change',
                    'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']

        self.qyxx_b_c = self.parse(pageSoup=self.reg_soup,
                                   tag='table',
                                   attrs={'id': 'table_bg'},
                                   key_list=key_list)

    def member_execute(self, id):
        """主要成员信息 """

        data = {
            'method': 'baInfo',
            'maent.pripid': id,
            'czmk': 'czmk2',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:
            self.bei_an_soup = soup     # 保存备案信息soup对象，用于分支机构。

            key_list = ['xuhao', 'person_name', 'p_position']
            # key_list = ['序号', '姓名', '职位']

            self.qyxx_member = self.parse(pageSoup=self.reg_soup,
                                          tag='table',
                                          attrs={'id': 'table_ry1'},
                                          key_list=key_list)

    # 分支机构信息
    def branch_execute(self, id):
        """分支机构信息"""

        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']

        self.qyxx_branch = self.parse(pageSoup=self.bei_an_soup,
                                      tag='table',
                                      attrs={'id': 'table_fr2'},
                                      key_list=key_list)

    # ******动产抵押登记******
    def mortgage_basic_execute(self, id):
        """动产抵押登记信息"""

        data = {
            'method': 'dcdyInfo',
            'maent.pripid': id,
            'czmk': 'czmk4',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority',
                        'amount', 'status', 'gongshiriqi', 'detail']
            # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'
            # '被担保债权数额'	'状态'	'公示日期'	'详情']

            self.qyxx_mortgage_basic = self.parse(pageSoup=soup,
                                                  tag='table',
                                                  attrs={'id': 'table_dc'},
                                                  key_list=key_list)

    # ******股权出资登记信息******
    def pledge_execute(self, id):
        """股权出资登记信息"""

        data = {
            'method': 'gqczxxInfo',
            'maent.pripid': id,
            'czmk': 'czmk4',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                        'plede_amount', 'brower', 'brower_id_card',
                        'reg_date', 'status', 'gongshiriqi', 'changes']
            # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额',
            # '质权人', '证件号码','股权出质设立登记日期', '状态', '公示日期', '变化情况']

            self.qyxx_pledge = self.parse(pageSoup=soup,
                                          tag='table',
                                          attrs={'id': 'table_gq'},
                                          key_list=key_list)

    # ******行政处罚信息******
    def adm_punishment_execute(self, id):
        """行政处罚信息"""

        data = {
            'method': 'cfInfo',
            'maent.pripid': id,
            'czmk': 'czmk3',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority',
                        'pun_date', 'gongshiriqi', 'detail']
            # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容',
            # '作出行政处罚决定机关名称','作出行政处罚决定日期','公示日期','详情']

            self.qyxx_adm_punishment = self.parse(pageSoup=soup,
                                                  tag='table',
                                                  attrs={'id': 'table_gscfxx'},
                                                  key_list=key_list)

    # ******经营异常信息******
    def abnormal_execute(self, id):
        """经营异常信息"""

        data = {
            'method': 'jyycInfo',
            'maent.pripid': id,
            'czmk': 'czmk6',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:
            key_list = ['xuhao', 'reason', 'date_occurred',
                        'reason_out', 'date_out', 'authority']
            # key_list = ['序号', '列入异常原因', '列入日期',
            # '移出异常原因', '移出日期', '作出决定机关']

            self.qyxx_abnormal = self.parse(pageSoup=soup,
                                            tag='table',
                                            attrs={'id': 'table_yc'},
                                            key_list=key_list)

    # ******严重违法信息******
    def black_info_execute(self, id):
        """严重违法信息"""

        data = {
            'method': 'yzwfInfo',
            'maent.pripid': id,
            'czmk': 'czmk14',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:
            key_list = ['xuhao', 'reason_in', 'date_in',
                        'reason_out','date_out','authority']
            # key_list = ['序号','列入严重违法失信企业名单原因','列入日期',
            # '移出严重违法失信企业名单原因','移出日期','作出决定机关']

            self.qyxx_black_info = self.parse(pageSoup=soup,
                                              tag='table',
                                              attrs={'id': 'table_wfxx'},
                                              key_list=key_list)

    # ******抽查检查信息******
    def spot_check_execute(self, id):
        """抽查检查信息"""

        data = {
            'method': 'ccjcInfo',
            'maent.pripid': id,
            'czmk': 'czmk7',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            key_list = ['xuhao', 'authority', 'spot_type', 'spot_date',
                        'spot_result']
            # key_list = ['序号','检查实施机关','类型','日期','结果']

            self.qyxx_spot_check = self.parse(pageSoup=soup,
                                              tag='table',
                                              attrs={'id': 'table_ccjc'},
                                              key_list=key_list)

    # ******股权冻结信息******
    def stock_freeze_execute(self, id):
        """司法股权冻结信息"""

        data = {
            'method': 'sfgsInfo',
            'maent.pripid': id,
            'czmk': 'czmk17',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number',
                        'status', 'detail']
            # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',
            # '协助公示通知书文号',	'状态',	'详情']

            self.qyxx_stock_freeze = self.parse(pageSoup=soup,
                                                tag='table',
                                                attrs={'id': 'table_gqdj'},
                                                key_list=key_list)

    # ******股东变更信息******
    def stockholder_change_execute(self, id):
        """司法股东变更登记信息"""

        data = {
            'method': 'sfgsbgInfo',
            'maent.pripid': id,
            'czmk': 'czmk18',
            'random': str(int(time.time() * 1000))
        }

        resp = url_requests.post(url=self.url,
                                 data=data,
                                 headers=self.headers)

        soup = BeautifulSoup(resp.content, 'lxml')

        if soup:

            key_list = ['xuhao','person','stock','person_get','court','detail']
            # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']

            self.qyxx_stockholder_change = self.parse(pageSoup=soup,
                                                      tag='table',
                                                      attrs={'id':
                                                                 'table_gdbg'},
                                                      key_list=key_list)

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, id, click_id):
        if self.qyxx_mortgage_basic:

            data = {
                'method': 'dcdyDetail',
                'maent.pripid': id,
                'maent.xh': click_id,
                'random': str(int(time.time() * 1000))
            }

            resp = url_requests.post(url=self.url,
                                     data=data,
                                     headers=self.headers)

            soup = BeautifulSoup(resp.content, 'lxml')

            if soup:
                self.mortgage_soup = soup
                soups = soup.find_all('table', {'class': 'detailsList'})

                for each_soup in soups:
                    if '动产抵押登记信息' in each_soup.text:
                        info = self.parse(pageSoup=each_soup)
                        if info:
                            self.mortgage_reg_num = info[0]['登记编号']
                            info[0] = common.c_mortgage_dict(info[0])
                            self.qyxx_c_mortgage.extend(info)
                        break

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, id, click_id):

        soups = self.mortgage_soup.find_all('table', {'class': 'detailsList'})
        for each_soup in soups:
            if '被担保债权概况' in each_soup.text:
                info = self.parse(pageSoup=each_soup)
                info[0]['mortgage_reg_num'] = self.mortgage_reg_num
                info[0] = common.s_creditor_dict(info[0])
                self.qyxx_s_creditor.extend(info)
                break

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, id, click_id):

        key_list = ['xuhao', 'mortgage_name', 'belongs',
                    'information', 'mortgage_range']
        # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']

        info = self.parse(pageSoup=self.mortgage_soup,
                          tag='table',
                          attrs={'id': 'table_dywgk'},
                          key_list=key_list)

        for each_info in info:
            each_info['mortgage_reg_num'] = self.mortgage_reg_num

        self.qyxx_mortgage.extend(info)

def main(**kwargs):

    id = kwargs.get('id_tag')
    all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute', 'member_execute',
        'branch_execute', 'adm_punishment_execute', 'abnormal_execute',
        'mortgage_basic_execute', 'pledge_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

    credit = CompanyInfo()
    # 工商公示
    loop = True  # 判断一次是否吊销，已吊销，则loop=False
    active = True  # 默认未吊销
    for each in all_execute[:-3]:
        print "%s %s %s" % ("*" * 20, each, "*" * 20)
        getattr(credit, each)(id)
        # businessInfo.pledge_execute(req_data)
        if credit.qyxx_basicinfo:
            while loop:
                loop = False
                if '已吊销' in credit.qyxx_basicinfo[0]['check_type']:
                    active = False
        if not active:
            break

    # 动产抵押物详情
    if credit.qyxx_mortgage_basic:
        for each_mort in credit.qyxx_mortgage_basic:
            onclick = each_mort['detail'].split("'")[1]
            for each in all_execute[-3:]:
                print '%s %s %s' % ('*' * 20, each, '*' * 20)
                getattr(credit, each)(id, onclick)

    results = credit.returnData()

    print "finished ..."

    return results

if __name__ == '__main__':
    # 运行时可冲sichuan_query.py中加载mainId 主函数

    name = [u'攀枝花市攀创科技开发有限公司',  # 动产抵押
            u'四川意思房产营销策划有限公司',
            u'汉源县川汉木业有限责任公司',  # 对应id[0]
            u'南充市高坪区小龙镇红心网吧',
            u'成都运筹帷幄酒业有限公司']

    id = ['511823000002012111600021',
          '511600000002014022400020', # 广安摩尔春天百货有限公司  黑名单(严重违法)
          '5104000000083691'] # 攀枝花市攀创科技开发有限公司   动产抵押

    main(id_tag=id[2])