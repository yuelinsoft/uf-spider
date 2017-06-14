# -*- coding: utf-8 -*-
"""
    create in 2016.12.20

    @author: "lijianbin"

    行政处罚，经营异常，严重违法需要有额外的网址访问
"""


from __future__ import unicode_literals
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common.page_parse import CreditInfo


class CompanyInfo(CreditInfo):
    """继承信用信息类

    """

    def __init__(self, url):
        super(CompanyInfo, self).__init__() # 继承父类的__init__
        self.mortgage_reg_num = None    # 存动产抵押登记编号
        self.url = url

    def basicinfo_execute(self, page_soup):

        soup = page_soup.find('table', {'class': 'tableYyzz'})

        if soup:
            td = soup.find_all('td')
            info = {}
            for each_td in td:
                key_value = each_td.text.split('：')
                if key_value[0]:
                    key = key_value[0][1:].strip()
                    value = key_value[1].strip()
                    info[key] = value
            info = common.basicinfo_dict(info, '上海市')
            self.qyxx_basicinfo.append(info)

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, page_soup):
        key_list = ['xuhao', 's_h_name', 's_h_type',
                    's_h_id_type', 's_h_id', 'detail']
        soup = page_soup.find('div', {'id': 'layout-01_01_02'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_s_h.extend(info)

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, page_soup):
        key_list = ['reason', 'before_change',
                    'after_change', 'date_to_change']
        soup = page_soup.find('div', {'id': 'layout-01_01_03'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_b_c.extend(info)

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, page_soup):

        soup = page_soup.find('div', {'id': 'layout-01_02_01'})
        if soup:
            soup = soup.find('table', {'class': 'dlPiece'})

            td = soup.find_all('td')

            for each in td:
                info = {}
                li = each.find_all('li')    # 'person_name', 'p_position'
                info['person_name'] = li[0].text.strip()
                info['p_position'] = li[1].text.strip()
                self.qyxx_member.append(info)

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, page_soup):

        soup = page_soup.find('div', {'id': 'layout-01_02_02'})
        if soup:
            soup = soup.find('table', {'class': 'dlPiece2'})

            td = soup.find_all('td')

            for each in td:
                info = {}
                li = each.find_all('li')  # 'company_num', 'company_name', 'authority'
                info['company_name'] = li[0].text.strip()
                info['company_num'] = li[1].text.split('：')[1].strip()
                info['authority'] = li[2].text.split('：')[1].strip()
                self.qyxx_branch.append(info)

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, page_soup):

        soup = page_soup.find('div', {'id': 'layout-01_04_01'})
        if soup:
            key_list = ['xuhao', 'mortgage_reg_num', 'date_reg',
                        'authority', 'amount', 'status', 'gsrq', 'xiangqing']

            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_mortgage_basic.extend(info)

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, page_soup):

        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                    'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'gongshiriqi', 'changes']
        soup = page_soup.find('div', {'id': 'layout-01_03_01'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_pledge.extend(info)

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, page_soup):

        url = self.url.split('&')[0] + '&tabPanel=03'

        headers = {
            'Host': 'sh.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36'),
            'Referer': 'http://sh.gsxt.gov.cn/notice/search/ent_info_list'
        }

        resp = url_requests.get(url, headers=headers, proxies=proxies)

        page_soup = BeautifulSoup(resp.content, 'lxml')
        key_list = ['xuhao', 'pun_number', 'reason', 'fines',
                    'authority', 'pun_date', 'gongshiriqi', 'detail']
        info = CreditInfo.parse(page_soup, 'table', {'class': 'tableG'},
                                key_list=key_list)

        self.qyxx_adm_punishment.extend(info)

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, page_soup):

        url = self.url.split('&')[0] + '&tabPanel=04'

        headers = {
            'Host': 'sh.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36'),
            'Referer': 'http://sh.gsxt.gov.cn/notice/search/ent_info_list'
        }

        resp = url_requests.get(url, headers=headers, proxies=proxies)

        page_soup = BeautifulSoup(resp.content, 'lxml')
        key_list = ['xuhao', 'reason', 'date_occurred',
                    'reason_out', 'date_out', 'authority']
        info = CreditInfo.parse(page_soup, 'table', {'class': 'tableG'},
                                key_list=key_list)

        self.qyxx_adm_punishment.extend(info)

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, page_soup):

        url = self.url.split('&')[0] + '&tabPanel=05'

        headers = {
            'Host': 'sh.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36'),
            'Referer': 'http://sh.gsxt.gov.cn/notice/search/ent_info_list'
        }

        resp = url_requests.get(url, headers=headers, proxies=proxies)

        page_soup = BeautifulSoup(resp.content, 'lxml')
        key_list = ['xuhao', 'reason_in', 'date_in',
                    'reason_out', 'date_out', 'authority']

        info = CreditInfo.parse(page_soup, 'table', {'class': 'tableG'},
                                key_list=key_list)

        self.qyxx_black_info.extend(info)

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, page_soup):

        soup = page_soup.find('div', {'id': 'layout-01_08_01'})
        if soup:
            key_list = ['xuhao', 'authority', 'spot_type', 'spot_date',
                        'spot_result']
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_spot_check.extend(info)

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, page_soup):

        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number',
                    'status', 'detail']
        soup = page_soup.find('div', {'id': 'layout-06_01_01'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_stock_freeze.extend(info)

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, page_soup):

        key_list = ['xuhao', 'person', 'stock', 'person_get', 'court',
                    'detail']
        soup = page_soup.find('div', {'id': 'layout-06_02_01'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_stockholder_change.extend(info)

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, mortgage_soup):

        soup = mortgage_soup.find_all('div', {'class': 'content2'})

        for each_soup in soup:
            if '动产抵押登记信息' in each_soup.text:

                info = self.parse(each_soup)
                if info != []:
                    self.mortgage_reg_num = info[0]['登记编号']

                    info[0] = common.c_mortgage_dict(info[0])

                    self.qyxx_c_mortgage.extend(info)
                break

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, mortgage_soup):

        soup = mortgage_soup.find_all('div', {'class': 'content2'})

        for each_soup in soup:
            if '被担保债权概况信息' in each_soup.text:
                info = self.parse(each_soup)
                if info != []:
                    info[0]['mortgage_reg_num'] = self.mortgage_reg_num

                    info[0] = common.s_creditor_dict(info[0])

                    self.qyxx_s_creditor.extend(info)
                break

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, mortgage_soup):
        soup = mortgage_soup.find_all('div', {'class': 'content2'})

        key_list = ['xuhao', 'mortgage_name', 'belongs',
                    'information', 'mortgage_range']

        for each_soup in soup:
            if '抵押物概况信息' in each_soup.text:
                info = self.parse(each_soup, key_list=key_list)
                if info != []:
                    info[0]['mortgage_reg_num'] = self.mortgage_reg_num

                    self.qyxx_mortgage.extend(info)
                break


def main(**kwargs):

    url = kwargs.get('id_tag')
    global proxies
    proxies = kwargs.get('proxies')
    headers = {
        'Host': 'sh.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.99 Safari/537.36'),
        'Referer': 'http://sh.gsxt.gov.cn/notice/search/ent_info_list'
    }

    resp = url_requests.get(url, headers=headers, proxies=proxies)

    page_soup = BeautifulSoup(resp.content, 'lxml')
    if len(resp.content) < 1000:
        url = page_soup.find('script').text.split("'")[1]
        resp = url_requests.get(url, headers=headers, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
    all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute', 'member_execute',
        'branch_execute', 'adm_punishment_execute', 'abnormal_execute',
        'mortgage_basic_execute', 'pledge_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
    ]

    mortgage_execute = [
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

    credit = CompanyInfo(url)  # 实例化
    for each in all_execute:
        print "Executing: %s" % each
        getattr(credit, each)(page_soup)
        # businessInfo.pledge_execute(page_soup)

    if credit.qyxx_mortgage_basic:
        for each in credit.qyxx_mortgage_basic:
            url = ('http://sh.gsxt.gov.cn/notice/notice/view_mortage?uuid'
                   '=') + each['xiangqing'].split("'")[1]

            resp = url_requests.get(url, headers=headers, proxies=proxies)

            mortgage_soup = BeautifulSoup(resp.content, 'lxml')

            for each_mort in mortgage_execute:
                print "Executing: %s" % each_mort
                getattr(credit, each_mort)(mortgage_soup)
                # credit.c_mortgage_execute(page_soup)
    results = credit.returnData()

    return results


if __name__ == '__main__':
    proxies = {
        'http': 'http://119.52.11.14:9999',
        'https': 'http://119.52.11.14:9999'
    }
    # b_list = 'http://sh.gsxt.gov.cn/notice/notice/view?uuid=nfc_corvFBy8Fg0k5uDN0lj0TmX2wm5v&tab=01'  # 万臣塑料制品（上海）有限公司（变更信息）
    # b_list = 'http://sh.gsxt.gov.cn/notice/notice/view?uuid=X2DSjivNBIeOQ.In8V3f1ABK44lqvLHF&tab=01' # 上海新亚电子开关厂有限公司（动产抵押登记信息）
    # b_list = 'http://sh.gsxt.gov.cn/notice/notice/view?uuid=9DfasM8QpxmXGIvtlYlbd1zueJbXekPt&tab=01' # 上海雪纯洗涤有限公司（股权出质登记）
    # b_list = ('http://sh.gsxt.gov.cn/notice/notice/view?uuid'
    #           '=ocWbkyycilfD0tELjB.zCdBH5PwUvLku&tab=01')  # 上海诚讯自动化技术装备有限公司(股东  翻页)
    # b_list = 'http://sh.gsxt.gov.cn/notice/notice/view?uuid=.9hSOfdfnXFEGBGxHtrZJTDEvtmAo694&tab=01' # 上海华爱门诊部有限公司（行政处罚）
    b_list = 'http://sh.gsxt.gov.cn/notice/notice/view?uuid=YueKBFLXXkz36u_C73kDDwSuSG.AdVcU&tab=01' # 上海紫欢服装有限公司（经营异常 ）
    # b_list = 'http://sh.gsxt.gov.cn/notice/notice/view?uuid=VgYaGdm2x7kZgvWlQJza8J.uLViHlZh0&tab=01' # 上海丽圣杰纳品牌管理有限公司（分支机构，股东信息）
    main(id_tag=b_list, proxies=proxies)