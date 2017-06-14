# -*- coding: utf-8 -*-
"""
    __author__ = 'lijianbin'

    深圳信用网企业信息查询脚本
"""


from __future__ import unicode_literals
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import common, url_requests
from EnterpriseCreditCrawler.common.uf_exception import IpRefused


def get_info(pageSoup, keyword_list, key_list):
    """深圳信用网，获取上下结构排列的信息内容。

    用于这些方法：s_h_execute， member_execute, c_mortgage_execute


    :param pageSoup: 包含所需内容的BeautifulSoup对象。
    :param keyword_list: 关键字（表名）列表，以兼容可能同一个内容出现多种不同的名称。
                            如 ['股东登记信息', '股东信息']
    :param key_list: 表头关键字列表， 如 [股东名称， 出资额， 出资比例]
                                  or ['share_holder_name', 'share_holder_cap',
                                      'share_holder_ptg']
    :return: 字典列表， 如 [{}, {}, {}]
    """

    # 注意：提示信息里左右结构也能用这种标签去查找，但是不能用这个函数,用get_taps
    tables = pageSoup.find_all('tr', {'style': 'font-weight:bold;'})
    values = pageSoup.find_all('tr', {'style': 'width:930px;'})
    value = None
    for i, each_table in enumerate(tables):
        table_name = each_table.find('a', class_='sjli')
        if table_name:
            table_name = table_name.text.strip()

        if table_name in keyword_list:
            value = values[i]
            break
        else:
            value = None

    if value:
        # 在大的'tr', {'style': 'width:930px;'}标签下再找出所有的tr标签，第一行为字段名
        values = value.find_all('tr')
        result = []
        if len(values) > 1:
            values = values[1:]
            for each_value in values:
                tds = each_value.find_all('td', {'align': 'left'})
                info = {}
                for i, value in enumerate(tds):
                    info[key_list[i]] = value.text.replace(
                                            '[点击查看开办企业情况]', '').strip()

                result.append(info)

            return result
        else:
            return []
    else:
        return []

def get_taps(pageSoup, keyword_list, key_list):
    """用法与参数含义同get_info

    用于这些方法：pledge_execute， court_execute，

    :param pageSoup:
    :param keyword_list:
    :param key_list:
    :return:
    """

    tables = pageSoup.find_all('tr', {'style': 'font-weight:bold;'})
    values = pageSoup.find_all('tr', {'style': 'width:930px;'})
    value = None
    for i, each_table in enumerate(tables):
        table_name = each_table.find('a', class_='sjli')
        if table_name:
            table_name = table_name.text.strip()
        if table_name in keyword_list:
            values = values[i]
            break
        else:
            continue
    if value:
        # 在大的'tr', {'style': 'width:930px;'}标签下再找出所有的tr标签，一行一个字段
        tr = values.find_all('tr')
        i = 0
        info = {}
        result = []
        for value in tr:
            info[key_list[i]] = value.find_all('td')[-1].text.strip()
            i += 1
            if i == len(key_list):
                result.append(info)
                info = {}
                i = 0
            else:
                continue
        return result
    else:
        return []


class Business():

    def __init__(self):
        self._results = {}  # 用来保存8个表的数据，没有的则为 []

    def basicInfo_execute(self, pageSoup):
        """基本信息下面左右样式的全部一次性拿下，然后按key取值。

        :return:
        """
        info_list = []  # 保存结果

        keys = pageSoup.find_all('td',
                                 {'style': 'background-color:rgb(243, 243, '
                                           '243);width:180px;'})
        if not keys:
            raise IpRefused("访问频繁或访问间隔时间太短！".encode('utf-8'))
        basic_info = {}
        for each_key in keys:
            key_value = {
                each_key.text.strip(): each_key.next_sibling.text.strip()
            }
            basic_info.update(key_value)

        if pageSoup.find(text=r'已载入异常经营名录') or pageSoup.find(
                text=r'[该企业已列入经营异常名录]，'):
            basic_info['警示信息'] = '是'
        else:
            basic_info['警示信息'] = '否'

        if pageSoup.find(text=r'[该企业已吊销]'):
            basic_info['企业登记状态'] = '吊销'

        if pageSoup.find(text=r'非正常'):
            basic_info['纳税人状态'] = '非正常'

        dict_keyword = {
            'reg_num': ['注册号',],
            'unin_credit_num': ['统一社会信用代码',],
            'father_company': ['隶属企业名称',],
            'company_name': ['企业名称', '名称'],
            'owner': ['法定代表人','负责人', '经营者', '执行事务合伙人', '股东',
                      '投资人', '执行合伙人', '首席代表'],
            'address': ['住所','营业场所'],
            'start_date': ['成立日期',],
            'check_date': ['核准日期',],
            'fund_cap': ['认缴注册资本总额',],
            'company_type': ['企业类型',],
            'business_area': ['经营范围',],
            'business_reg_status': ['企业登记状态',],
            'annual_check': ['年检情况',],
            'annual_report': ['年报情况',],
            'taxer_number': ['纳税人识别号',],
            'taxer_status': ['纳税人状态',],
            'org_number': ['机构代码',],
            'annual_check_date': ['年检日期',],
            'annual_check_date_to': ['年检期限',],
            'abandon': ['废置情况',],
            'warning': ['警示信息',],
            'social_security_numb': ['社保单位编号',],
            'social_security_s_yr': ['投保起始年',],
            'social_security_s_mh': ['投保起始月',],
            's_s_curreny_status': ['当前状态',],
            's_s_population_total': ['参保总人数',],
            's_s_population_old': ['养老参保人数',],
            's_s_population_med': ['医疗参保人数',],
            's_s_population_hurt': ['工伤参保人数',],
            's_s_population_unem': ['失业参保人数',],
            'accumulation_fund_num': ['单位公积金号',],
            'a_f_start_date': ['单位开户时间',],
            'a_f_start_date_to': ['公积金缴存截至时间',],
            'work_area': ['经营面积',],
            'workers': ['从业人数',],
            'business_lim': ['营业期限',],
        }

        basic_info = common.judge_keyword(basic_info, dict_keyword)
        basic_info['locate'] = '深圳市'

        # 标准化数据处理（一系列替换）
        if basic_info.has_key('owner'):
            basic_info['owner'] = basic_info.pop('owner').replace(
                                            '[点击查看任职企业情况]', '')

        info_list.append(basic_info)

        return info_list

    def b_c_execute(self, pageSoup):
        """企业变更信息(偏偏这个比较特殊，目前单独写)

        :param pageSoup:
        :return:
        """

        info_list = []  # 保存结果

        keyword_list = ['企业变更信息', ]

        key_list = ['change_num', 'date_time', 'reason']

        table = pageSoup.find('table', {'id': 'Table123'})

        if not table:
            return []

        table_name = [x for x in table.find('li', {'class':
                                                 'current'})._all_strings()][0]

        if table_name in keyword_list:
            div = table.find('div', {'id': 'listdiv'})
            values = div.find_all('tr')
            if len(values) > 1:
                values = values[1:]
            else:
                return []
            for each_value in values:
                tds = each_value.find_all('td')[:-1]
                info = {}
                for i, value in enumerate(tds):
                    info[key_list[i]] = value.text.strip()
                info_list.append(info)

            return info_list
        else:
            return []

    def s_h_execute(self, pageSoup):
        """股东信息

        :param pageSoup:
        :return:
        """

        keyword_list = ['股东登记信息',]

        key_list = ['share_holder_name', 'share_holder_cap',
                    'share_holder_ptg']

        info_list= get_info(pageSoup, keyword_list, key_list)

        return info_list

    def abnormal_execute(self, pageSoup):
        """经营异常信息

        :param pageSoup:
        :return:
        """

        info_list = []  # 保存结果

        keyword_list = ['商事主体经营异常名录信息', ]

        key_list = ['action_list', 'reason', 'date_time']

        pageSoup = pageSoup.find('table', {'id':'Table4'})
        if not pageSoup:
            return []
        tables = pageSoup.find_all('tr', {'style': 'font-weight:bold;'})
        values = pageSoup.find_all('tr', {'style': 'width:930px;'})
        value = None
        for i, each_table in enumerate(tables):
            table_name = each_table.find('a', class_='sjli').text.strip()
            if table_name in keyword_list:
                value = values[i]
                break
            else:
                value = None

        if value:
            keys = value.find_all('td',
                                    {'style': 'background-color:rgb(243, 243, '
                                               '243);width:180px;'})
            info = {}
            for i, each_key in enumerate(keys):
                key_value = {
                    key_list[i]: each_key.next_sibling.text.strip()
                }
                info.update(key_value)
            info_list.append(info)

        return info_list

    def member_execute(self, pageSoup):
        """主要成员信息

        :param pageSoup:
        :return:
        """
        keyword_list = ['成员登记信息']

        key_list = ['person_name', 'p_position']

        info_list = get_info(pageSoup, keyword_list, key_list)

        return info_list

    def pledge_execute(self, pageSoup):
        """锁定限制信息(股权出资登记)

        :param pageSoup:
        :return:
        """
        keyword_list = ['锁定限制信息',]
        key_list = ['reason', 'date_range', 'status', 'details', 'comm'] #有序

        info_list = get_taps(pageSoup, keyword_list, key_list)

        return info_list

    def court_execute(self, pageSoup):
        """被执行人案件信息

        :param pageSoup:
        :return:
        """
        keyword_list = ['被执行人案件信息', ]
        key_list = ['case_name', 'case_num', 'case_evd_num', 'case_date',
                    'case_court', 'judge', 'judge_phone', 'case_status',
                    'case_amd', 'case_comment']

        info_list = get_taps(pageSoup, keyword_list, key_list)

        return info_list

    def c_mortgage_execute(self, pageSoup):
        """动产抵押登记信息

        :param pageSoup:
        :return:
        """
        keyword_list = ['动产抵押登记信息', ]
        key_list = ['mortgage_reg_num', 'loaner', 'borrower', 'mortgage_name',
                    'mortgage_quant', 'contract_number', 'date_teg',
                    'reg_status']

        info_list = get_info(pageSoup, keyword_list, key_list)

        return info_list

def main(**kwargs):

    link = kwargs.get('id_tag')
    proxies = kwargs.get('proxies')
    # proxies = None  # 暂不使用动态IP

    # 第三步，get请求用第二步得到的连接，但是要设置headers里面的Referer参数
    keyword = link['company_name'].__repr__().replace('\\', '%')[2:-1]
    # print keyword
    headers = {
        'Host':'www.szcredit.org.cn',
        'Referer':'https://www.szcredit.org.cn/web/gspt/newGSPTList.aspx?'
                   'keyword=' + keyword,
                    # ('%u6DF1%u5733%u5E02%u6C47%u6D77%u8BDA%u54C1%u7F51
                    # %u7EDC%u79D1%u6280%u6709%u9650%u516C%u53F8',)
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/53.0.2785.143 Safari/537.36')
    }

    html = url_requests.get(url=link['link'], headers=headers, proxies=proxies)
    # print response.text
    pageSoup = BeautifulSoup(html.text, 'lxml')

    tableDict = {
        'basicInfo_execute' : 'qyxx_sz_basicinfo',
        'b_c_execute': 'qyxx_sz_b_c',
        's_h_execute': 'qyxx_sz_s_h',
        'abnormal_execute': 'qyxx_sz_abnormal',
        'member_execute': 'qyxx_sz_member',
        'pledge_execute': 'qyxx_sz_pledge',
        'court_execute': 'qyxx_sz_court',
        'c_mortgage_execute': 'qyxx_sz_c_mortgage',
    }
    business = Business()
    for each_execute in tableDict.keys():
        print "%s %s %s" % ("*" * 20, each_execute, "*" * 20)
        business._results[tableDict[each_execute]] = getattr(business,
                                                   each_execute)(pageSoup)
        # basicinfo = business.c_mortgage_execute(pageSoup=pageSoup)

    return business._results

if __name__ == '__main__':
    #
    # # '深圳市汇海诚品网络科技有限公司'
    # link = {'company_name': '深圳市汇海诚品网络科技有限公司',
    #          'link': 'https://www.szcredit.org.cn/web/gspt/newGSPTDetail3'
    #                  '.aspx?ID=18c950ac1d574d7a89e1bc85ad2edac0'}
    #
    # # '深圳市海怡小汽车出租有限公司  pledge_execute 被执行人
    # link = {'company_name': '深圳市海怡小汽车出租有限公司',
    #          'link': 'https://www.szcredit.org.cn/web/gspt/newGSPTDetail3'
    #                  '.aspx?ID=e93ec0c603094bef903a67d4d2c114dd'}

    # '深圳市华星光电技术有限公司' c_mortgage  动产抵押
    link = {'company_name': '深圳市华星光电技术有限公司',
             'link': 'https://www.szcredit.org.cn/web/gspt/newGSPTDetail3'
                     '.aspx?ID=8b6bc52967b24ca2bd64e24414bce059'}

    main(id_tag=link)