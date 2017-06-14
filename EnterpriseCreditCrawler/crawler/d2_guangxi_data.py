# -*- coding: utf-8 -*-
"""
    @author: "kexh"
    @updater: "kexh"(2016.12.28)
        [修改为滑块验证方式后，网站内容也已经改版]
"""
from __future__ import unicode_literals
import re
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common.page_parse import CreditInfo

class CompanyInfo(CreditInfo):
    """继承信用信息类

    """
    def __init__(self, params):
        super(CompanyInfo, self).__init__() # 继承父类的__init__
        self.mortgage_reg_num = None    # 存动产抵押登记编号
        self.params = params

    def basicinfo_execute(self, page_soup_origin):
        url = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml'
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        self.basic_content = resp.content
        # print type(self.basic_content)
        page_soup = BeautifulSoup(self.basic_content, 'lxml')
        soup = page_soup.find('table', {'class': 'qy-list'})

        if soup:
            td = soup.find_all('td')
            info = {}
            for each_td in td:
                key_value = each_td.text.split('：')
                if key_value[0]:
                    key = key_value[0].strip()
                    value = key_value[1].strip()
                    info[key] = value
            info = common.basicinfo_dict(info, '广西省')
            self.qyxx_basicinfo.append(info)
            uniscid_flag = page_soup_origin.findAll(name='a', attrs={"href": re.compile(r'uniscid')})
            self.regno = self.qyxx_basicinfo[0]["reg_num"]
            if uniscid_flag != []:
                p = 'regno=\w+'
                s0 = uniscid_flag[0]['href']
                if re.search(p, s0) != None:
                    s = re.search(p, s0).group()
                    self.regno = s.split('=')[1]

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!touzirenInfo.dhtml'
        self.params["regno"] = self.regno
        self.params["urltag"] = '2'
        self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')

        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        if soup:
            try:
                key_list = ['xuhao', 's_h_name', 's_h_type',
                            's_h_id_type', 's_h_id', 'detail']
                info = CreditInfo.parse(page_soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)
            except:
                key_list = ['xuhao', 's_h_name', 's_h_type',
                            's_h_id_type', 's_h_id']
                info = CreditInfo.parse(page_soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)

            self.qyxx_s_h.extend(info)

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!xj_biangengFrame.dhtml'
        self.params["regno"] = self.regno
        self.params["urlflag"] = '5'
        self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
        key_list = ['xuhao', 'reason', 'before_change',
                    'after_change', 'date_to_change']
        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)

            self.qyxx_b_c.extend(info)

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml'
        self.params["regno"] = self.regno
        self.params["urltag"] = '3'
        self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')

        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        if soup:
            tb = soup.find_all('table')
            for each in tb:
                info = {}
                td = each.find_all('td')  # 'person_name', 'p_position'
                info['person_name'] = td[0].text.strip()
                info['p_position'] = td[1].text.strip() if len(td)>1 else ''
                self.qyxx_member.append(info)

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!fzjgFrame.dhtml'
        self.params["regno"] = self.regno
        self.params["urltag"] = '4'
        self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        if soup:
            td = soup.find_all('table')
            for each in td:
                info = {}
                td = each.find_all('td')  # 'company_num', 'company_name', 'authority'
                info['company_name'] = td[0].text.strip()
                info['company_num'] = td[1].text.split('：')[1].strip() if len(td)>1 else ''
                info['authority'] = td[2].text.split('：')[1].strip() if len(td)>2 else ''
                self.qyxx_branch.append(info)
            # print self.qyxx_branch

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml'
        # self.params["regno"] = self.regno
        self.params["urltag"] = '12'
        # self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        # print soup
        if soup:
            key_list = ['xuhao', 'mortgage_reg_num', 'date_reg',
                        'authority', 'amount', 'status', 'gsrq', 'xiangqing']
            info = CreditInfo.parse(soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)

            self.qyxx_mortgage_basic.extend(info)
            # print self.qyxx_mortgage_basic

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml'
        # self.params["regno"] = self.regno
        self.params["urltag"] = '13'
        # self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')

        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                    'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'gongshiriqi', 'changes']
        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        # print soup
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)
            self.qyxx_pledge.extend(info)
        # print self.qyxx_pledge

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn//gdgq/gdgqAction!xj_qyxzcfFrame.dhtml'
        # self.params["regno"] = self.regno
        self.params["urltag"] = '14'
        # self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')

        key_list = ['xuhao', 'pun_number', 'reason', 'fines',
                    'authority', 'pun_date', 'gongshiriqi', 'detail']
        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)

            self.qyxx_adm_punishment.extend(info)

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml'
        self.params["regno"] = self.regno
        self.params["urlflag"] = '8'
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
        # print page_soup
        key_list = ['xuhao', 'reason', 'date_occurred', 'authority_occurred',
                    'reason_out', 'date_out', 'authority']
        info = CreditInfo.parse(page_soup, 'table', {'class': 'table-result'},
                                key_list=key_list)

        self.qyxx_adm_punishment.extend(info)

    # QYXX_BLACK_INFO严重违法信息
    def black_info_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml'
        # self.params["regno"] = self.regno
        self.params["urltag"] = '9'
        self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
        key_list = ['xuhao', 'reason_in', 'date_in',
                    'reason_out', 'date_out', 'authority']

        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        # print soup
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)

        self.qyxx_black_info.extend(info)

    # QYXX_SPOT_CHECK抽查检验信息
    def spot_check_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/gsgs/gsxzcfAction!xj_list_ccjcxx.dhtml'
        # self.params["regno"] = self.regno
        self.params["urltag"] = '10'
        self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')
        soup = page_soup.find('div', {'class': 'qyqx-detail'})
        if soup:
            key_list = ['xuhao', 'authority', 'spot_type', 'spot_date',
                        'spot_result']
            info = CreditInfo.parse(soup, 'table', {'class': 'table-result'},
                                    key_list=key_list)

            self.qyxx_spot_check.extend(info)

    # QYXX_STOCK_FREEZE股权冻结信息
    def stock_freeze_execute(self, page_soup):
        p = u'股权冻结'
        s = self.basic_content
        if re.search(p, s) != None:
            raise ValueError('stock_freeze_execute !!!!')

    # QYXX_STOCKHOLDER_CHANGE股权更变信息
    def stockholder_change_execute(self, page_soup):
        url = 'http://gx.gsxt.gov.cn/newChange/newChangeAction!getTabForNB_new.dhtml'
        # self.params["regno"] = self.regno
        self.params["urltag"] = '15'
        self.params["flag_num"] = '2'
        # self.params["ent_id"] = self.params["entId"]
        headers = {
            'Host': 'gx.gsxt.gov.cn',
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/54.0.2840.99 Safari/537.36')
        }
        resp = url_requests.get(url, headers=headers, params=self.params, proxies=proxies)
        page_soup = BeautifulSoup(resp.content, 'lxml')

        key_list = ['xuhao', 'person', 'stock', 'person_get', 'court',
                    'detail']
        soup = page_soup.find('div', {'id': 'layout-06_02_01'})
        if soup:
            info = CreditInfo.parse(soup, 'table', {'class': 'tableG'},
                                    key_list=key_list)

            self.qyxx_stockholder_change.extend(info)

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, mortgage_soup):
        soup = mortgage_soup.find_all('div', {'style': 'width:800px;height:600px;'})

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
        soup = mortgage_soup.find_all('div', {'style': 'width:800px;height:600px;'})

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
        soup = mortgage_soup.find_all('div', {'style': 'width:800px;height:600px;'})

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
    url = 'http://gx.gsxt.gov.cn' + kwargs.get('id_tag')
    params = {}
    for kv in url.split("?")[1].split("&"):
        params[kv.split("=")[0]] = kv.split("=")[1]
    # print params
    # print url
    global proxies
    # 广西暂时不使用代理
    proxies = None
    proxies = kwargs.get('proxies')
    headers = {
        'Host': 'gx.gsxt.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/54.0.2840.99 Safari/537.36')
    }
    resp = url_requests.get(url, headers=headers, params=params, proxies=proxies)
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
    credit = CompanyInfo(params)  # 实例化
    loop = True  # 判断一次是否吊销，已吊销，则loop=False
    active = True  # 默认未吊销
    for each in all_execute:
        print "%s %s %s" % ("*" * 20, each, "*" * 20)
        getattr(credit, each)(page_soup)
        if credit.qyxx_basicinfo:
            while loop:
                loop = False
                if '已吊销' in credit.qyxx_basicinfo[0]['check_type']:
                    active = False
        if not active:
            break

    if credit.qyxx_mortgage_basic:
        for each in credit.qyxx_mortgage_basic:
            url = 'http://gx.gsxt.gov.cn'+each['xiangqing'].split("'")[1]
            resp = url_requests.get(url, headers=headers,proxies=proxies)

            mortgage_soup = BeautifulSoup(resp.content, 'lxml')

            for each_mort in mortgage_execute:
                getattr(credit, each_mort)(mortgage_soup)
    results = credit.returnData()

    # print 'Success!'

    return results

if __name__ == '__main__':
    b_list = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!queryEntIndexInfo.dhtml?entId=24504000000034485&clear=true&urltag=1&urlflag=0&credit_ticket=6A77C1733C7B757BC3144EDE944C88A8'#广西苍梧电力集团有限公司东安供电所
    # b_list = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!queryEntIndexInfo.dhtml?entId=145000100046237539&clear=true&urltag=1&urlflag=0&credit_ticket=884B20B30E54B413E734F491B09C0B88'#广西南宁益龙云天置业投资有限公司
    # b_list = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!queryEntIndexInfo.dhtml?entId=24501000000759573&clear=true&urltag=1&urlflag=0&credit_ticket=2F2A1E8A4F7DAC1194EDADA58742972A'#广西医药有限责任公司
    # b_list = 'http://gx.gsxt.gov.cn/gjjbj/gjjQueryCreditAction!queryEntIndexInfo.dhtml?entId=24503000000065808&clear=true&urltag=1&urlflag=0&credit_ticket=9C5A3443E5A5A46FBA5545D4B98D0314'#桂林金福盛祥房地产开发有限责任公司

    results = main(id_tag=b_list)
    common.for_print(results)

