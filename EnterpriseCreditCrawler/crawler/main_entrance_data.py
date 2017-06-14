# -*- coding: utf-8 -*-
"""
    search enterprise credit detail-information

"""


from __future__ import unicode_literals
import re
import time
import json
import base64
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo


def format_date(string):
    '''将时间戳转换成日期，时间戳是13位其实只需要10位。

    :rtype: string like '2017-01-01'
    '''
    if not string:
        return ''
    elif len(str(string)) == 13:
        string = str(string)[:-3]

    st = time.localtime(int(string))
    date = time.strftime('%Y-%m-%d', st)

    return date

def get_headers():
    '''随机获取userAgent'''

    headers = {
        'Host': 'www.gsxt.gov.cn',
        'Referer': 'http://www.gsxt.gov.cn/corp-query-search-1.html',
        'User-Agent': url_requests.random_userAgent()
    }

    return headers

def get_data(urls, keyword):
    '''获取版块信息

    :param urls: List, 该列表来源于企业信息页面的源代码中，是每个版块的url后缀列表。
    :param keyword: str， 板块关键字
    :return: List，所需板块的数据
    '''

    result = []

    url = None
    for each in urls:
        if keyword in each:
            url = 'http://www.gsxt.gov.cn' + each.split('"')[1].strip()
            break
    if url:
        headers = get_headers()
        response = url_requests.get(url=url, headers=headers, proxies=proxies)
        json_data = json.loads(response.content)
        all_data = json_data.get('data')  # 先获取第一页的数据
        total_page = json_data.get('totalPage')
        if total_page > 1:
            for page in range(1, total_page):
                form_data = {
                    'draw': 1,
                    'start': page * 5,
                    'length': 5
                }
                headers = get_headers()
                response = url_requests.post(url=url,
                                             data=form_data,
                                             headers=headers,
                                             proxies=proxies)
                json_data = json.loads(response.content)
                data = json_data.get('data')
                all_data.extend(data)  # 将翻页获取的数据合并
        result = all_data
    return result


class CompanyInfo(CreditInfo):
    """继承信用信息类

    """

    def __init__(self):
        super(CompanyInfo, self).__init__() # 继承父类的__init__
        self.mortgage_reg_num = ''    # 存动产抵押登记编号

    def basicinfo_execute(self, **kwargs):

        soup = kwargs.get('soup')
        basicinfo = soup.find('div', class_='overview')
        keys = basicinfo.find_all('dt')
        values = basicinfo.find_all('dd')
        info = {}
        for i, each_key in enumerate(keys):
            key = each_key.text.replace('\n', '')\
                                .replace('\r', '')\
                                .replace('\t', '')\
                                .strip()[:-1]
            try:
                value = values[i].text.replace('\n', '')\
                                        .replace('\r', '')\
                                        .replace('\t', '')\
                                        .strip()
            except IndexError:
                value = ''
            info[key] = value
        self.qyxx_basicinfo.append(common.basicinfo_dict(info, ''))

    # QYXX_S_H登记信息（股东信息,翻页已解决）
    def s_h_execute(self, **kwargs):
        key_list = ['s_h_name', 's_h_type',
                    's_h_id_type', 's_h_id', 'detail']
        all_url = kwargs.get('all_url')
        keyword = '股东信息'

        data = get_data(urls=all_url, keyword=keyword)
        result_list = []
        for each in data:
            item = {}
            item['s_h_name'] = each.get('inv', '')
            s_h_type = each.get('invType_CN', '')  # 包含标签的,
            if s_h_type:
                s_h_type = base64.b64decode(s_h_type.split(
                                                        '>')[1].split('<')[0])
            item['s_h_type'] = s_h_type
            item['s_h_id_type'] = each.get('blicType', '')
            s_h_id = each.get('bLicNo', '') # 取出第一段base64编码再反编译出id
            if s_h_id:
                s_h_id = base64.b64decode(s_h_id.split('>')[1].split('<')[0])
            item['s_h_id'] = s_h_id
            item['detail'] = each
            result_list.append(item)
        self.qyxx_s_h = result_list

    # QYXX_B_C登记信息（更变信息,翻页已解决）
    def b_c_execute(self, **kwargs):
        '''变更信息，个体工商户变更信息'''

        key_list = ['reason', 'before_change',
                    'after_change', 'date_to_change']
        all_url = kwargs.get('all_url')

        keyword = 'alterInfoUrl'
        if '个体工商户'  in self.qyxx_basicinfo[0]['company_type']:
            keyword = 'gtAlertInfoUrl'

        data = get_data(urls=all_url, keyword=keyword)
        result_list = []
        for each in data:
            item = {}
            reason = each.get('altItem_CN', '')
            if reason:
                reason = base64.b64decode(reason.split('>')[1].split('<')[0])
            item['reason'] = reason
            item['before_change'] = each.get('altBe', '')
            item['after_change'] = each.get('altAf', '')
            item['date_to_change'] = format_date(each.get('altDate', ''))
            result_list.append(item)

        self.qyxx_b_c = result_list

    # QYXX_MEMBER备案信息（主要人员信息, 查看全部已解决）
    def member_execute(self, **kwargs):
        key_list = ['xuhao', 'person_name', 'p_position']

        all_url = kwargs.get('all_url')

        keyword = 'keyPersonUrl'
        if '个体工商户' in self.qyxx_basicinfo[0]['company_type']:
            keyword = 'gtkeyPersonUrl'

        url = None
        for each in all_url:
            if keyword in each:
                url = 'http://www.gsxt.gov.cn' + each.split('"')[1].strip()
                break
        if url:
            headers = get_headers()
            response = url_requests.get(url=url, headers=headers,
                                        proxies=proxies)
            json_data = json.loads(response.content)
            all_data = json_data.get('data')
            total_page = json_data.get('totalPage')
            per_page = json_data.get('perPage')    # 每页可获取的条目数
            if total_page > 1:
                for page in range(1, total_page):
                    form_data = {
                        # 'draw': 1,
                        'start': page * per_page,
                        # 'length': 5
                    }
                    headers = get_headers()
                    response = url_requests.get(url=url,
                                                 params=form_data,
                                                 headers=headers,
                                                proxies=proxies)
                    json_data = json.loads(response.content)
                    data = json_data.get('data')
                    all_data.extend(data)
            result_list = []
            for each in all_data:
                item = {}
                name = each.get('name', '')
                if name:
                    name = base64.b64decode(name.split('>')[1].split('<')[0])
                item['person_name'] = name
                item['p_position'] = each.get('position_CN', '').strip()
                result_list.append(item)
            self.qyxx_member = result_list

    # QYXX_BRANCH备案信息（分支机构信息, 查看全部已解决）
    def branch_execute(self, **kwargs):
        key_list = ['xuhao', 'company_num',
                    'company_name', 'authority']

        all_url = kwargs.get('all_url')

        keyword = 'branchUrlAll'
        # if '个体工商户' in self.qyxx_basicinfo[0]['company_type']:
        #     keyword = 'gtkeyPersonUrl'
        url = None
        for each in all_url:
            if keyword in each:
                url = 'http://www.gsxt.gov.cn' + each.split('"')[1].strip()
                break
        if url:
            headers = get_headers()
            response = url_requests.get(url=url, headers=headers,
                                        proxies=proxies)
            url = 'http://www.gsxt.gov.cn' + re.search(
                'branchUrlData ="(.*?)"', response.content,
                re.S).group(1)
            headers = get_headers()
            response = url_requests.get(url=url, headers=headers,
                                        proxies=proxies)
            json_data = json.loads(response.content)
            all_data = json_data.get('data')
            total_page = json_data.get('totalPage')
            per_page = json_data.get('perPage')  # 每页可获取的条目数
            if total_page > 1:
                for page in range(1, total_page):
                    form_data = {
                        # 'draw': 1,
                        'start': page * per_page,
                        # 'length': 5
                    }
                    headers = get_headers()
                    response = url_requests.get(url=url,
                                                params=form_data,
                                                headers=headers,
                                                proxies=proxies)
                    json_data = json.loads(response.content)
                    data = json_data.get('data')
                    all_data.extend(data)
            result_list = []
            for each in all_data:
                item = {}
                item['company_num'] = each.get('regNo', '')
                item['company_name'] = each.get('brName', '')
                item['authority'] = each.get('regOrg_CN', '')
                result_list.append(item)
            self.qyxx_branch = result_list

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, **kwargs):
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg',
                    'authority', 'amount', 'status',
                    'gongshiriqi', 'detail']
        all_url = kwargs.get('all_url')

        keyword = 'mortRegInfoUrl'
        # if '个体工商户' in self.qyxx_basicinfo[0]['company_type']:
        #     keyword = 'gtAlertInfoUrl'
        data = get_data(urls=all_url, keyword=keyword)
        result_list = []
        for each in data:
            item = {}
            item['mortgage_reg_num'] = each.get('morRegCNo', '')
            item['date_reg'] = format_date(each.get('regiDate', ''))
            item['authority'] = each.get('regOrg_CN', '')
            item['amount'] = each.get('priClaSecAm', '')
            if item['amount']:
                item['amount'] = str(item['amount']) + '万' + each.get(
                                                        'regCapCur_CN', '')
            item['status'] = each.get('type', '')
            s_type = {
                '1': '有效',
                '2': '无效'
            }
            item['status'] = s_type[item['status']]
            item['detail'] = each
            result_list.append(item)

        self.qyxx_mortgage_basic = result_list

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, **kwargs):
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                    'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'gongshiriqi', 'changes']
        all_url = kwargs.get('all_url')
        keyword = 'stakQualitInfoUrl'
        data = get_data(all_url, keyword)
        result_list = []
        for each in data:
            item = {}
            item['reg_code'] = each.get('equityNo', '')
            item['pleder'] = each.get('pledgor', '')
            item['id_card'] = each.get('pledBLicNo', '')
            item['plede_amount'] = each.get('impAm', '')
            item['brower'] = each.get('impOrg', '')
            item['brower_id_card'] = each.get('impOrgId', '')
            item['reg_date'] = each.get('equPleDate', '')
            if item['reg_date']:
                item['reg_date'] = format_date(item['reg_date'])
            item['status'] = each.get('type', '')
            s_type = {
                '1': '有效',
                '2': '无效'
            }
            item['status'] = s_type[item['status']]
            result_list.append(item)
        self.qyxx_pledge = result_list

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, **kwargs):
        key_list = ['xuhao', 'pun_number', 'reason', 'fines',
                    'authority', 'pun_date', 'gongshiriqi', 'detail']
        all_url = kwargs.get('all_url')
        keyword = 'punishmentDetailInfoUrl'
        data = get_data(all_url, keyword)

        result_list = []
        for each in data:
            item = {}
            item['pun_number'] = each.get('penDecNo', '')
            item['reason'] = each.get('illegActType', '')
            item['fines'] = each.get('penContent', '')
            item['authority'] = each.get('penAuth_CN', '')
            item['pun_date'] = format_date(each.get('penDecIssDate', ''))
            result_list.append(item)
        self.qyxx_adm_punishment = result_list

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, **kwargs):
        key_list = ['xuhao', 'reason', 'date_occurred',
                        'reason_out', 'date_out', 'authority']
        c_type = {
            '个体工商户': 'indBusExcepUrl',
            '农民专业合作社': 'argBusExcepUrl',
            '农民专业合作社分支机构': 'argBranchBusExcepUrl'
        }
        all_url = kwargs.get('all_url')
        keyword = 'entBusExcepUrl'
        for each in c_type.keys():
            if each in self.qyxx_basicinfo[0]['company_type']:
                keyword = c_type['each']
                break
        data = get_data(urls=all_url, keyword=keyword)

        result_list = []
        for each in data:
            item = {}
            item['reason'] = each.get('speCause_CN', '')
            item['date_occurred'] = each.get('abntime', '')
            item['reason_out'] = each.get('remExcpRes_CN', '')
            item['date_out'] = each.get('remDate', '')
            item['authority'] = each.get('decOrg_CN', '')
            result_list.append(item)
        self.qyxx_abnormal = result_list

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, **kwargs):
        key_list = ['xuhao', 'reason_in', 'date_in',
                        'reason_out','date_out','authority']
        all_url = kwargs.get('all_url')
        keyword = 'IllInfoUrl'
        data = get_data(urls=all_url, keyword=keyword)
        if data:
            raise ValueError('there is black info')

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, **kwargs):
        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date',
                        'spot_result']
        all_url = kwargs.get('all_url')
        keyword = 'spotCheckInfoUrl'
        data = get_data(urls=all_url, keyword=keyword)
        result_list = []
        for each in data:
            item = {}
            item['authority'] = each.get('insAuth_CN', '')
            item['spot_type'] = each.get('insType_CN', '')
            item['spot_date'] = format_date(each.get('insDate', ''))
            item['spot_result'] = each.get('insRes_CN', '')
            result_list.append(item)
        self.qyxx_spot_check = result_list

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, **kwargs):
        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number',
                        'status', 'detail']
        all_url = kwargs.get('all_url')
        keyword = 'judiciaryStockfreezePersonUrl'

        data = get_data(urls=all_url, keyword=keyword)

        result_list = []
        for each in data:
            item = {}
            item['person'] = each.get('inv', '')
            item['stock'] = each.get('froAm', '')
            if item['stock']:
                item['stock'] = str(item['stock']) + '万' + each.get(
                                                            'regCapCur_CN', '')
            item['court'] = each.get('froAuth', '')
            item['notice_number'] = each.get('executeNo', '')
            item['status'] = each.get('frozState_CN', '')
            result_list.append(item)
        self.qyxx_stock_freeze = result_list

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, **kwargs):
        '''字段信息已经改变，原来的表结构已经不能反映现在的情况了。'''

        key_list = ['xuhao','person','stock','person_get','court','detail']

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, **kwargs):

        mortReg_Id = kwargs.get('mortReg_Id')
        url = ('http://www.gsxt.gov.cn/corp-query-entprise-info'
               '-getMortRegCancelInfo-%s.html') % mortReg_Id
        headers = get_headers()
        response = url_requests.get(url, headers=headers, proxies=proxies)
        json_data = json.loads(response.content)
        data = json_data.get('data')

        for each in data:
            item = {}
            item['mortgage_reg_num'] = each.get('morRegCNo', '')
            self.mortgage_reg_num = each.get('morRegCNo', '')
            item['date_reg'] = format_date(each.get('regiDate', ''))
            item['authority'] = each.get('regOrg_CN', '')
            item['mortgage_type'] = ''
            item['amount'] = ''
            item['time_range'] = ''
            item['mortgage_range'] = ''
            self.qyxx_c_mortgage.append(item)

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, **kwargs):

        mortReg_Id = kwargs.get('mortReg_Id')
        url = ('http://www.gsxt.gov.cn/corp-query-entprise-info-'
               'mortCreditorRightInfo-%s.html') % mortReg_Id
        headers = get_headers()
        response = url_requests.get(url, headers=headers, proxies=proxies)
        json_data = json.loads(response.content)
        data = json_data.get('data')
        for each in data:
            item = {}
            item['mortgage_reg_num'] = self.mortgage_reg_num
            item['mortgage_type'] = each.get('priClaSecKind_CN', '')
            item['amount'] = each.get('priClaSecAm', '')
            item['mortgage_range'] = each.get('warCov', '')
            item['time_range'] = format_date(each.get('pefPerForm', '')) \
                                 + '至' + \
                                 format_date(each.get('pefPerTo', ''))

            self.qyxx_s_creditor.append(item)

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, **kwargs):
        key_list = ['xuhao', 'mortgage_name', 'belongs',
                    'information', 'mortgage_range']
        mortReg_Id = kwargs.get('mortReg_Id')
        url = ('http://www.gsxt.gov.cn/corp-query-entprise-info'
               '-mortGuaranteeInfo-%s.html') % mortReg_Id
        headers = get_headers()
        response = url_requests.get(url, headers=headers, proxies=proxies)
        json_data = json.loads(response.content)
        data = json_data.get('data')
        item_list = []
        for each_item in data:
            item = {}
            item['mortgage_reg_num'] = self.mortgage_reg_num
            item['mortgage_name'] = each_item.get('guaName', '')
            item['belongs'] = each_item.get('own', '')
            item['information'] = each_item.get('guaDes', '')
            item['mortgage_range'] = each_item.get('remark', '')

            item_list.append(item)

        self.qyxx_mortgage.extend(item_list)


def main(**kwargs):

    all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute', 'member_execute',
        'branch_execute', 'mortgage_basic_execute', 'pledge_execute',
        'adm_punishment_execute', 'abnormal_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

    # 这次访问仅能获取基本信息
    url = kwargs.get('id_tag')
    global proxies
    proxies = kwargs.get('proxies')

    headers = get_headers()
    response = url_requests.get(url=url, headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.content, 'lxml')

    # 获取除基本信息以外的所有包含url的字符串集合
    mainContent = soup.find('div', class_='mainContent')

    # 下面返回是一个列表
    all_url_strings = mainContent.text.split('var')

    # 执行获取信息的操作
    company_info = CompanyInfo()

    # 独立获取营业执照信息（用到soup）
    print "Executing: %s" % 'basicinfo_execute'
    company_info.basicinfo_execute(soup=soup)

    # 从股东信息开始获取其他版块信息(动产抵押详情除外)
    for each in all_execute[1:-3]:
        print "Executing: %s" % each
        getattr(company_info, each)(all_url=all_url_strings)

    # 如果存在动产抵押信息，则执行后三个来获取详细信息。
    if company_info.qyxx_mortgage_basic:
        for each_mort in company_info.qyxx_mortgage_basic:
            mortReg_Id = each_mort.get('detail')['morReg_Id']
            # 传入此id
            for each in all_execute[-3:]:
                print "Executing: %s" % each
                getattr(company_info, each)(mortReg_Id=mortReg_Id)

    result = company_info.returnData()

    return result


def start(**kwargs):
    """ """


if __name__ == '__main__':

    search_link = (
'http://www.gsxt.gov.cn/%7BEJLQyzHdacUUigzBUtjHmt0qKm8WyQu8_WXKOnyvSj03SG9ZkyXUwBqTidcCDuDgf_itdUoTjF_n1zoIf0lepAwRzx3k9nyhe4ImOYOIGgTEExJG5qs02-hmKqtiqBrZ2FAbxS5VBAFGnI1g3-2oxQ-1488875478380%7D'
    )
    main(id_tag=search_link)