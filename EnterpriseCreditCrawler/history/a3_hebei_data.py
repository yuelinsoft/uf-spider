# -*- coding: utf-8 -*-
"""
    __author__ = 'lijianbin'
    the same as 上海（如果这里改动了，可能上海的也需要更改。）
"""

from __future__ import  unicode_literals
from EnterpriseCreditCrawler.common.page_parse import CreditInfo
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common import common
from bs4 import BeautifulSoup


class CompanyInfo(CreditInfo):
    """继承信用信息类，获取企业的各项信息。

    """

    def __init__(self):
        super(CompanyInfo, self).__init__() # 继承父类的__init__
        self.mortgage_reg_num = None    # 存动产抵押登记编号

    def basicinfo_execute(self, pageSoup):

        info = self.parse(pageSoup,
                          tag='div',
                          attrs={'rel':'layout-01_01'})
        if info != []:
            info[0] = common.basicinfo_dict(info[0],u'河北省')

        self.qyxx_basicinfo = info

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, pageSoup):
        key_list = ['xuhao', 'reason','date_occurred',
                    'reason_out','date_out','authority']
        self.qyxx_abnormal = self.parse(pageSoup,
                                        attrs={'id': 'exceptTable'},
                                        key_list=key_list)

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, pageSoup):
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authirty',
                    'pun_date', 'xiangqing']
        self.qyxx_adm_punishment = self.parse(pageSoup,
                                              attrs={'id':'punishTable'},
                                              key_list=key_list)

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, pageSoup):
        key_list = ['reason', 'before_changes',
                    'after_changes', 'date_to_changes']
        self.qyxx_b_c = self.parse(pageSoup,
                                   attrs={'id': 'alterTable'},
                                   key_list=key_list)

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, pageSoup):
        key_list = ['xuhao','company_num','company_name','authority']
        self.qyxx_branch = self.parse(pageSoup,
                                      attrs={'id': 'branchTable'},
                                      key_list=key_list)

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, pageSoup):
        key_list = ['xuhao','person_name','p_position']
        self.qyxx_member = self.parse(pageSoup,
                                      attrs={'id': 'memberTable'},
                                      key_list=key_list)

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, pageSoup):
        key_list = ['xuhao','mortgage_reg_num','date_reg',
                    'authority','amount','status','xiangqing']
        self.qyxx_mortgage_basic = self.parse(pageSoup,
                                              attrs={'id': 'mortageTable'},
                                              key_list=key_list)

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, pageSoup):
        key_list = ['xuhao','reg_code','pleder','id_card','plede_amount',
                    'brower','brower_id_card','reg_date',
                    'staues','changes']
        self.qyxx_pledge = self.parse(pageSoup,
                                      attrs={'id': 'pledgeTable'},
                                      key_list=key_list)

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, pageSoup):
        key_list = ['s_h_type', 's_h_name', 's_h_id_type',
                    's_h_id', 'xiangqing']
        self.qyxx_s_h = self.parse(pageSoup,
                                   attrs={'id': 'investorTable'},
                                   key_list=key_list)

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, pageSoup):
        key_list = ['xuhao','authority','spot_type','spot_date','spot_result']
        self.qyxx_spot_check = self.parse(pageSoup,
                                          attrs={'id': 'spotcheckTable'},
                                          key_list=key_list)

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, pageSoup):
        key_list = ['xuhao','person','stock','court',
                    'notice_number','statues','xiangqing']
        self.qyxx_stockholder_change = self.parse(pageSoup,
                                                  tag='div',
                                                  attrs={'rel':"layout-06_01"},
                                                  key_list=key_list)

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, pageSoup):
        key_list = ['xuhao','person','stock','person_get','court','xiangqing']
        self.qyxx_stockholder_change = self.parse(pageSoup,
                                                  tag='div',
                                                  attrs={'rel':'layout-06_01'},
                                                  key_list=key_list)

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, pageSoup):
        key_list = ['xuhao','reason_in','date_in','reason_out',
                    'date_out','authority']
        self.qyxx_black_info = self.parse(pageSoup,
                                          attrs={'id': 'blackTable'},
                                          key_list=key_list)


    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        tables = pageSoup.find('div', class_='detail-info')
        tables = tables.find_all('table')
        info = []
        for each in tables:
            if '动产抵押登记信息' in each.find('tr').text:
                info = self.parse(each)
                if info != []:
                    self.mortgage_reg_num = info[0]['登记编号']
                break
        info[0] = common.c_mortgage_dict(info[0])
        self.qyxx_c_mortgage.extend(info)

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        tables = pageSoup.find('div', class_='detail-info')
        tables = tables.find_all('table')
        info = []
        for each in tables:
            if '被担保债权概况' in each.find('tr').text:
                info = self.parse(each)
                if info != []:
                    info[0]['mortgage_reg_num'] = self.mortgage_reg_num
                break
        info[0] = common.s_creditor_dict(info[0])
        self.qyxx_s_creditor.extend(info)

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):
        key_list = ['xuhao','mortgage_name','belongs',
                    'information','mortgage_range']
        table = pageSoup.find('table', {'id':'mortgageGuaTable'})
        info = self.parse(table, key_list=key_list)
        for each in info:
            each['mortgage_reg_num'] = self.mortgage_reg_num
        self.qyxx_mortgage.extend(info)


def main(**kwargs):
    """主函数，包含逻辑流程"""

    company_info = CompanyInfo()

    headers_info = {
        'Connection': 'keep-alive',
        'Host': 'www.hebscztxyxx.gov.cn',
        'Referer': 'http://www.hebscztxyxx.gov.cn/notice/search/ent_info_list',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/44.0.2403.155 Safari/537.36',
    }

    # 工商公示信息
    url = kwargs.get('id_tag')

    html = url_requests.get(url, headers=headers_info)

    soup = BeautifulSoup(html.content, 'lxml')

    executeA = [
        'basicinfo_execute', 'branch_execute','black_info_execute',
        'abnormal_execute', 'adm_punishment_execute',
        'b_c_execute', 'member_execute', 'mortgage_basic_execute',
        'pledge_execute',
        's_h_execute', 'spot_check_execute'
    ]
    for c in executeA:
        print "%s %s %s" % ("*" * 20, c, "*" * 20)
        getattr(company_info, c)(soup)

    # 司法协助公示信息
    executeB = [
        'stock_freeze_execute', 'stockholder_change_execute'
    ]

    url = url[:-2] + '06'

    html = url_requests.get(url, headers=headers_info)

    soup = BeautifulSoup(html.content, 'lxml')

    for c in executeB:
        print "%s %s %s" % ("*" * 20, c, "*" * 20)
        getattr(company_info, c)(soup)

    # 动产抵押详情
    execute_d = ['c_mortgage_execute', 's_creditor_execute',
                 'mortgage_execute']
    if company_info.qyxx_mortgage_basic != []:
        for each in company_info.qyxx_mortgage_basic:
            url = each['xiangqing'].split('>>>')[1]
            html = url_requests.get(url, headers=headers_info)
            soup = BeautifulSoup(html.content, 'lxml')
            for c in execute_d:
                print "%s %s %s" % ("*" * 20, c, "*" * 20)
                getattr(company_info, c)(soup)

    # 汇总数据到字典
    results = company_info.returnData()

    return results


if __name__ == '__main__':
    # ['http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=C4A9swFBtC.BpVUfjj68HzHo1m3FCid4&tab=01', 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=MbjNfIgyeBxIRjE_GchUzadFBS_LMQUJ&tab=01']
    # b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=y.1zD2eUMazv4UxRfIwF765KcVNf6jVU&tab=01' # 石家庄悦森珠宝销售有限公司（变更信息，股东信息）
    # b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=SImc_ZtmZNduaTU5NNKzqCAGXWDGM3aD&tab=01' # 邯郸市第二钢铁厂（经营异常）
    # b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=ZRyrfPKQMy.Yap9BHZ0l4QXkQfOAwW4t&tab=01' # 石家庄双联复合肥有限责任公司（股权出质，主要人员【翻页】，分支机构（空））
    # b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=hB5rRpgbhndZR9wyija5SK8G5szIgm84&tab=01'  # 石家庄晓飞糖业有限公司（抵押物【翻页】,司法协助公示信息）
    b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=d8hXeeeCqpobmSp3rX788dpStLF6yAeo&tab=01' # 石家庄市矿区隆鑫棉线加工厂（抽查检验）
    # b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=DMurXixlluHKlZX86ivZsSdsjfELqLy7&tab=01' # 容城县靓点美妆日化店(行政处罚信息)
    # b_list = 'http://www.hebscztxyxx.gov.cn/notice/notice/view?uuid=TrB_ttQ5rp8V5GI4UYNRsYHKDmeYAzvt&tab=01' # 北国商城股份有限公司(分支机构)
    print main(id_tag=b_list)
