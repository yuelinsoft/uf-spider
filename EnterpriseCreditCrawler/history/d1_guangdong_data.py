# -*- coding:utf-8 -*-
"""
    __author__ = "lijianbin"

    广东省企业信用查询脚本，内含深圳部分（基本用不到）。
"""


from __future__ import unicode_literals

import re
import json
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo

def change_detail(url, params, cookies):
    """对于变更信息中查看变更前后资料的处理

    :param url:
    :param params:
    :param cookies:
    :return:
    """

    headers = {
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/54.0.2840.71 Safari/537.36'),
        'Host':'gsxt.gdgs.gov.cn',
    }
    html = url_requests.get(url,
                            params=params,
                            headers=headers,
                            cookies=cookies).text

    soup = BeautifulSoup(html, 'lxml')
    key_list = ['holderName', 'idCard']

    info = CreditInfo.parse(soup,
                            name='div', attrs={'id': 'jibenxinxi'},
                            key_list=key_list)
    info = str(info).decode('utf-8')

    return info

class BusinessInfo(CreditInfo):
    """工商公示信息类"""

    def __init__(self):
        super(BusinessInfo, self).__init__()
        self.headers = {
                'Host': 'gsxt.gdgs.gov.cn',
                'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                               'AppleWebKit/537.36 (KHTML, like Gecko) '
                               'Chrome/53.0.2785.143 Safari/537.36'),
                # 'Referer': 'http://gsxt.gdgs.gov.cn/'
            }
        self.cookies = None
        self.mortgage_reg_num = None    # 用来保存动产抵押登记编号

    # 登记信息部分
    def basicinfo_execute(self, data):
        '''
        :return: 基本信息 dict
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=entInfo')
        response = url_requests.post(url,
                                     headers=self.headers,
                                     data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('table', {'id': 'baseinfo'})
        Info = self.parse(soup,'table', {'id': 'baseinfo'})
        if Info:
            if Info[0].has_key('统一社会信用代码') and Info[0].has_key('注册号'):
                if Info[0]['统一社会信用代码'] == '':
                    Info[0]['统一社会信用代码'] = Info[0]['注册号']

            Info[0] = common.basicinfo_dict(Info[0], '广东省')

        self.qyxx_basicinfo = Info

    # 股东信息
    def s_h_execute(self, data):
        '''

        :param data: 包含企业id的query文件中返回的data
        :return:
        '''

        url = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/invInfoPage.html'
        data['pageNo'] = 1  # 虽然有分页，目前发现可一次全部返回
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)

        jsn = json.loads(response.text)
        if not jsn:
            return []
        else:
            list = {}
            if 'list' in jsn:
                list = jsn['list']  # 这里面包含了全部的数据，不管多少页，其长度就是股东个数
        # key_list = ['s_h_type', 's_h_name', 's_h_id_type', 's_h_id',
        #             'xiangqing']
        # key_list = ['股东类型', '股东', '股东证件类型', '股东证件号', 详情]
        for info in list:
            info['s_h_type'] = info.pop('invType', '')
            info['s_h_name'] = info.pop('inv', '')
            info['s_h_id_type'] = info.pop('certName', '')
            info['s_h_id'] = info.pop('certNo', '')

        self.qyxx_s_h = list

    # 变更信息
    def b_c_execute(self, data):
        '''
        :return: 变更信息
        '''
        url = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/entChaPage'
        data['pageNo'] = 1
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        # print response.text
        jsn = json.loads(response.text)
        if jsn.has_key('list'):
            list = jsn['list'] # 这里面包含了全部的数据，不管多少页，其长度就是股东个数
        else:
            return []

        # key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        for info in list:

            info['reason'] = info.pop('altFiledName', '')
            info['date_to_change'] = info.pop('altDate', '')

            if info['altTable'] != 'BizindividualInvestor':
                info['before_change'] = info.pop('altBe', '')
                info['after_change'] = info.pop('altAf', '')
            else:
                before_params = {}
                after_params = {}
                # change_before
                before_params['oldHistNo'] = info['oldHistNo']
                before_params['altTable'] = info['altTable']
                before_params['entNo'] = info['entNo']
                before_params['regOrg'] = data['regOrg']
                before_url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity'
                              '/invastorOld.html')
                info['before_change'] = change_detail(before_url,
                                                      params=before_params,
                                                      cookies=response.cookies)
                # change_after
                after_params['newHistNo'] = info['newHistNo']
                after_params['altTable'] = info['altTable']
                after_params['entNo'] = info['entNo']
                after_params['regOrg'] = data['regOrg']
                after_url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity'
                              '/invastorNew.html')
                info['after_change'] = change_detail(after_url,
                                                      params=after_params,
                                                      cookies=response.cookies)
        self.qyxx_b_c = list

    # 备案信息——主要成员信息
    def member_execute(self, data):
        '''
        :return: 主要成员信息 list, 是 [姓名，职位] 列表
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=entCheckInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('div', {'id': 'zyry'})
        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']

        self.qyxx_member = self.parse(soup, 'div', {'id': 'zyry'},
                                  key_list=key_list)

    # 备案信息——分支机构信息
    def branch_execute(self, data):
        '''
        :return: 分支机构信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=entCheckInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('div', {'id': 'branch'})
        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        self.qyxx_branch = self.parse(soup, tag='div',
                          attrs={'id': 'branch'},
                          key_list=key_list)

    # 动产抵押登记
    def mortgage_basic_execute(self, data):
        '''
        :return: 动产抵押登记信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
              '.html?service=pleInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg',
                    'authority', 'amount', 'status', 'detail']
        # key_list = ['序号','登记编号','登记日期','登记机关','被担保债权数额','状态','详情']
        self.qyxx_mortgage_basic = self.parse(soup, key_list=key_list)

    # 股权出资登记信息
    def pledge_execute(self, data):
        '''
        :return: 股权出资登记信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=curStoPleInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                    'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '变化情况']

        self.qyxx_pledge = self.parse(soup, key_list=key_list)

    # 行政处罚信息
    def adm_punishment_execute(self, data):
        '''
        :return: 行政处罚信息
        '''

        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=cipPenaltyInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'pun_number', 'reason', 'fines',
                    'authority', 'pun_date', 'xiangqing']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','详情']
        self.qyxx_adm_punishment = self.parse(soup, key_list=key_list)

    # 经营异常信息
    def abnormal_execute(self, data):
        '''
        :return: 经营异常信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=cipUnuDirInfo')
        response = url_requests.post(url,
                                     headers=self.headers,
                                     data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'reason', 'date_occurred',
                    'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '移出异常原因', '移出日期', '作出决定机关（列出）']

        self.qyxx_abnormal = self.parse(soup, key_list=key_list)

    # 严重违法信息
    def black_info_execute(self, data):
        '''
        :return: 严重违法信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=cipBlackInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'reason_in', 'date_in',
                    'reason_out', 'date_out', 'authority']
        # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']

        self.qyxx_black_info = self.parse(soup, key_list=key_list)

    # 抽查检查信息
    def spot_check_execute(self, data):
        '''
        :return: 抽查检查信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
               '.html?service=cipSpotCheInfo')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'authority', 'spot_type',
                    'spot_date', 'spot_result']
        # key_list = ['序号','检查实施机关','类型','日期','结果']

        self.qyxx_spot_check = self.parse(soup, key_list=key_list)

    # 股权冻结信息
    def stock_freeze_execute(self, data):
        '''
        :return:
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/judiciaryAssist'
               '/judiciaryAssistInit.html ')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'person', 'stock', 'court',
                    'notice_number', 'status', 'xiangqing']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']

        self.qyxx_stock_freeze = self.parse(soup, key_list=key_list)

    # 股东变更信息
    def stockholder_change_execute(self, data):
        '''
        :return: 司法股东变更登记信息 or 行政处罚信息
        '''
        url = ('http://gsxt.gdgs.gov.cn/aiccips/sfGuQuanChange/guQuanChange'
               '.html')
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'person', 'stock',
                    'person_get', 'court', 'xiangqing']
        # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']

        self.qyxx_stockholder_change = self.parse(soup, key_list=key_list)

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        table = pageSoup.find_all('table', class_='detailsList')
        for each_table in table:
            if '动产抵押登记信息' in each_table.text:
                info = self.parse(each_table)
                if info != []:
                    self.mortgage_reg_num = info[0]['登记编号']
                    info[0] = common.c_mortgage_dict(info[0])
                    self.qyxx_c_mortgage.extend(info)
                break

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        table = pageSoup.find_all('table', class_='detailsList')
        for each_table in table:
            if '被担保债权概况' in each_table.text:
                info = self.parse(each_table)
                if info != []:
                    info[0] = common.s_creditor_dict(info[0])
                    info[0]['mortgage_reg_num'] = self.mortgage_reg_num
                    self.qyxx_s_creditor.extend(info)
                break

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):
        table = pageSoup.find_all('table', class_='detailsList')

        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information',
                    'mortgage_range']
        # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']

        for each_table in table:
            if '抵押物概况' in each_table.text:
                info = self.parse(each_table, key_list=key_list)
                info[0]['mortgage_reg_num'] = self.mortgage_reg_num
                self.qyxx_mortgage.extend(info)

class BusinessInfo1(CreditInfo):
    """
        网址中含有szcredit时用这个类

        注意：变更信息与行政处罚两项需要单独访问，且必须先访问行政处罚，再从html里获取信息
            访问变更信息，都是post请求
    """
    def __init__(self, link, cookies):
        """作用于行政处罚和变更信息"""
        super(BusinessInfo1, self).__init__()
        self.url = link
        self.headers = {
            'Host':'www.szcredit.com.cn',
            'Origin':'http://www.szcredit.com.cn',
            'Referer':link,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/54.0.2840.71 Safari/537.36',
            'X-MicrosoftAjax':'Delta=true',
            'X-Requested-With':'XMLHttpRequest'
        }
        self.cookies = cookies
        self.punishment_html = ''   # 声明这个变量是为了保存访问行政处罚时的html，
        # 以便于进一步访问变更信息，因为这两块单独出来了。


    # 登记信息部分
    def basicinfo_execute(self, pageSoup):
        '''
        :return: 基本信息 dict
        '''

        soup = pageSoup.find('div', {'id': 'jibenxinxi'})
        Info = self.parse(soup,'table', {'id': 'baseinfo'})
        if Info[0].has_key('统一社会信用代码') and Info[0].has_key('注册号')\
                and Info[0]['统一社会信用代码'] == '':
            Info[0]['统一社会信用代码'] = Info[0]['注册号']
        dict_keyword = dict(reg_num=['统一社会信用代码', u'注册号',
                                     u'注册号/统一社会信用代码'],
                            company_name=[u'名称', u'公司名称'],
                            owner=[u'法定代表人', u'负责人', u'股东', u'经营者',
                                   u'执行事务合伙人', u'投资人'],
                            address=[u'营业场所', u'经营场所', u'住所', u'住所/经营场所'],
                            start_date=[u'成立日期', u'注册日期'],
                            check_date=[u'核准日期', u'发照日期'],
                            fund_cap=[u'注册资本'],
                            company_type=[u'类型'], business_area=[u'经营范围'],
                            business_from=[u'经营期限自', u'营业期限自'],
                            check_type=[u'登记状态', u'经营状态'],
                            authority=[u'登记机关'], locate=[u'区域'])

        Info[0][u'区域'] = u'广东省'
        Info[0] = common.judge_keyword(Info[0], dict_keyword)

        self.qyxx_basicinfo = Info

    # 股东信息
    def s_h_execute(self, pageSoup):
        '''


        '''
        soup = pageSoup.find_all('table')[1]    # 第二个table标签是投资人信息
        table = soup.find_all('tbody')[0]   # 第二个table的第二个tbody标签是主体部分

        key_list = ['s_h_type', 's_h_name', 's_h_id_type', 's_h_id',
                    'xiangqing']
        # key_list = ['股东类型', '股东', '股东证件类型', '股东证件号', 详情]
        self.qyxx_s_h = self.parse(table, key_list=key_list)

    # 变更信息
    def b_c_execute(self, pageSoup):
        '''
        :return: 变更信息
        '''
        # 先从self.punishment_html里获取到data的参数

        EVENTARGUMENT = re.search('EVENTARGUMENT\|(.*?)\|',
                                  self.punishment_html, re.S).group(1)
        VIEWSTATE = re.search('VIEWSTATE\|(.*?)\|',
                                  self.punishment_html, re.S).group(1)
        VIEWSTATEGENERATOR = re.search('VIEWSTATEGENERATOR\|(.*?)\|',
                                  self.punishment_html, re.S).group(1)
        data = {
            'ScriptManager1': 'biangengxinxi|Timer2',
            '__EVENTTARGET': 'Timer2',
            '__EVENTARGUMENT': EVENTARGUMENT,
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            '__ASYNCPOST': 'true'
        }

        html = url_requests.post(self.url,
                                 data=data,
                                 headers=self.headers,
                                 cookies=self.cookies).text
        soup = BeautifulSoup(html, 'lxml')
        key_list = ['xuhao', 'reason', 'before_change',
                    'after_change', 'date_to_change']
        # key_list = ['序号', '变更事项', '变更前', '变更后', '变更日期']

        if soup:
            self.qyxx_b_c = self.parse(soup, key_list=key_list)

    # 备案信息——主要成员信息
    def member_execute(self, pageSoup):
        '''
        :return: 主要成员信息 list, 是 [姓名，职位] 列表
        '''
        soup = pageSoup.find('div', {'id': 'beianPanel'})
        soup = soup.find('table', {'id': 't30'})

        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']
        if soup:
            self.qyxx_member = self.parse(soup, key_list=key_list)

    # 备案信息——分支机构信息
    def branch_execute(self, pageSoup):
        '''
        :return: 分支机构信息
        '''
        soup = pageSoup.find('div', {'id': 'beianPanel'})
        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        if soup:
            self.qyxx_branch = self.parse(soup, 'table', {'id': 't31'},
                                          key_list=key_list)

    # 动产抵押登记
    def mortgage_basic_execute(self, pageSoup):
        '''
        :return: 动产抵押登记信息
        '''
        soup = pageSoup.find('div', {'id': 'dongchandiyaPanel'})
        # soup = soup.find('div', {'id': 'branch'})
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority',
                    'amount', 'status', 'detail']
        # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'详情']
        if soup:
            self.qyxx_mortgage_basic = self.parse(soup, key_list=key_list)

    # 股权出资登记信息
    def pledge_execute(self, pageSoup):
        '''
        :return: 股权出资登记信息
        '''
        soup = pageSoup.find('div', {'id': 'GQCZPanel'})
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                    'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '变化情况']
        if soup:
            self.qyxx_pledge = self.parse(soup, key_list=key_list)

    # 行政处罚信息
    def adm_punishment_execute(self, pageSoup):
        '''
        :return: 行政处罚信息
        '''
        # 先从pageSoup里获取到data的参数
        EVENTARGUMENT = pageSoup.find(id='__EVENTARGUMENT')['value'].strip()
        VIEWSTATE = pageSoup.find(id='__VIEWSTATE')['value'].strip()
        VIEWSTATEGENERATOR = pageSoup.find(
                                    id='__VIEWSTATEGENERATOR')['value'].strip()
        data = {
            'ScriptManager1': 'xingzhengchufa|Timer1',
            '__EVENTTARGET': 'Timer1',
            '__EVENTARGUMENT':EVENTARGUMENT,
            '__VIEWSTATE': VIEWSTATE,
            '__VIEWSTATEGENERATOR': VIEWSTATEGENERATOR,
            '__ASYNCPOST':'true'
        }

        self.punishment_html = url_requests.post(self.url,
                                                 data=data,
                                                 headers=self.headers,
                                                 cookies=self.cookies).text
        soup = BeautifulSoup(self.punishment_html, 'lxml')
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority',
                    'pun_date', 'xiangqing']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','详情']
        if soup:
            self.qyxx_adm_punishment = self.parse(soup, key_list=key_list)

    # 经营异常信息
    def abnormal_execute(self, pageSoup):
        '''
        :return: 经营异常信息
        '''
        soup = pageSoup.find('div', {'id': 'JYYCPanel'})
        key_list = ['xuhao', 'reason', 'date_occurred', 'reason_out',
                    'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '移出异常原因', '移出日期', '作出决定机关（列出）']

        if soup:
            self.qyxx_abnormal = self.parse(soup, key_list=key_list)

    # 严重违法信息
    def black_info_execute(self, pageSoup):
        '''
        :return: 严重违法信息
        '''
        soup = pageSoup.find('div', {'id': 'YZWFPanel'})
        key_list = ['xuhao', 'reason_in', 'date_in', 'reason_out',
                    'date_out', 'authority']
        # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']

        if soup:
            self.qyxx_black_info = self.parse(soup, key_list=key_list)

    # 抽查检查信息
    def spot_check_execute(self, pageSoup):
        '''
        :return: 抽查检查信息
        '''
        soup = pageSoup.find('div', {'id': 'CCJCPanel'})
        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date',
                    'spot_result','beizhu']
        # key_list = ['序号','检查实施机关','类型','日期','结果','备注']

        if soup:
            self.qyxx_spot_check = self.parse(soup, key_list=key_list)

    # 股权冻结信息
    def stock_freeze_execute(self, pageSoup):
        '''
        :return:
        '''

        # key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number',
        #             'status', 'xiangqing']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']
        pass

    # 股东变更信息
    def stockholder_change_execute(self, pageSoup):
        '''
        :return: 司法股东变更登记信息 or 行政处罚信息
        '''

        # key_list = ['xuhao', 'person', 'stock', 'person_get', 'court',
        #             'xiangqing']
        # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']

        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        qufenkuang = pageSoup.find('div', {'id': 'qufenkuang'})
        table = qufenkuang.find_all('table', class_='detailsList')
        for each_table in table:
            if '动产抵押登记信息' in each_table.text:
                info = self.parse(each_table)
                if info != []:
                    self.mortgage_reg_num = info[0]['登记编号']
                    info[0] = common.c_mortgage_dict(info[0])
                    self.qyxx_c_mortgage.extend(info)
                break

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        qufenkuang = pageSoup.find('div', {'id': 'qufenkuang'})
        table = qufenkuang.find_all('table', class_='detailsList')
        for each_table in table:
            if '被担保债权概况' in each_table.text:
                info = self.parse(each_table)
                if info != []:
                    info[0] = common.s_creditor_dict(info[0])
                    info[0]['mortgage_reg_num'] = self.mortgage_reg_num
                    self.qyxx_s_creditor.extend(info)
                break

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):
        qufenkuang = pageSoup.find('div', {'id': 'qufenkuang'})
        table = qufenkuang.find_all('table', class_='detailsList')

        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information',
                    'mortgage_range']
        # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']

        for each_table in table:
            if '抵押物概况' in each_table.text:
                info = self.parse(each_table, key_list=key_list)
                info[0]['mortgage_reg_num'] = self.mortgage_reg_num
                self.qyxx_mortgage.extend(info)

def guangdong(**kwargs):
    link = kwargs.get('id_tag')
    # 先访问query脚本返回的url获取其中的三个参数entNo， entType， regOrg，并组成data用于访问每个模块。
    headers = {
        'Host': 'gsxt.gdgs.gov.cn',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/53.0.2785.143 Safari/537.36'),
        'Referer': 'http://gsxt.gdgs.gov.cn/aiccips/main/initJyycInfoList.html'
    }
    response = url_requests.get(link, headers=headers, timeout=10)
    # print response.text
    soup = BeautifulSoup(response.text, 'lxml')
    req_data = {}
    req_data['entNo'] = soup.find('input', {'name': 'entNo'})['value']
    req_data['entType'] = soup.find('input', {'name': 'entType'})['value']
    req_data['regOrg'] = soup.find('input', {'name': 'regOrg'})['value']

    # 接着用这个req_data作为参数，传给每一个模块的url，获取信息。
    executeA = ['basicinfo_execute', 'abnormal_execute','black_info_execute',
                'adm_punishment_execute', 'b_c_execute',
                'branch_execute', 'member_execute', 'mortgage_basic_execute',
                'pledge_execute','s_h_execute', 'spot_check_execute',
                'stock_freeze_execute', 'stockholder_change_execute'
                ]

    execute_d = ['c_mortgage_execute', 's_creditor_execute',
                 'mortgage_execute'
                 ]

    businessInfo = BusinessInfo()
    loop = True  # 判断一次是否吊销，已吊销，则loop=False
    active = True  # 默认未吊销
    for each in executeA:
        print "%r %r %r" % ("*" * 20, each, "*" * 20)
        getattr(businessInfo, each)(req_data)
        # businessInfo.pledge_execute(req_data)
        if businessInfo.qyxx_basicinfo:
            while loop:
                loop = False
                if '已吊销' in businessInfo.qyxx_basicinfo[0]['check_type']:
                    active = False
        if not active:
            break

    "暂时未发现有动产抵押的"
    # 此处声明的三个变量是用于当有多个动产抵押项目的时候能把三个表的结果放到一个列表里面
    if businessInfo.qyxx_mortgage_basic:
        L = businessInfo.qyxx_mortgage_basic
        headers = {
            'Host': 'gsxt.gdgs.gov.cn',
            'Referer': link,
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/54.0.2840.71 Safari/537.36'
        }
        for dict in L:
            url = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity'
                   '/GSpublicityList.html')

            pleNo = dict['detail'].split("'")[1]

            data = {
                'service':'pleInfoData',
                'pleNo': pleNo,
                'entNo':req_data.get('entNo'),
                'entType':req_data.get('entType'),
                'regOrg':req_data.get('regOrg')
            }

            html = url_requests.post(url,
                                     data=data,
                                     headers=headers,
                                     cookies=response.cookies).text

            pageSoup = BeautifulSoup(html, 'lxml')

            for c in execute_d:
                print "%s %s %s" % ("*" * 20, c, "*" * 20)
                getattr(businessInfo, c)(pageSoup)

    results = businessInfo.returnData()

    return results

def shenzhen(**kwargs):
    link = kwargs.get('id_tag')

    headers = {
        'Host':'www.szcredit.com.cn',
        'Referer':'http://gsxt.gdgs.gov.cn/aiccips/CheckEntContext/showInfo'
                  '.html',
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 '
                     '(KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'
    }

    response = url_requests.get(link,
                                headers=headers)
    html = response.text
    # print html
    pageSoup = BeautifulSoup(html, 'lxml')

    # 必须先访问行政处罚在访问变更信息
    executeA = ['basicinfo_execute', 'abnormal_execute', 'black_info_execute',
                'adm_punishment_execute', 'b_c_execute',
                'branch_execute', 'member_execute', 'mortgage_basic_execute',
                'pledge_execute','s_h_execute', 'spot_check_execute',
                'stock_freeze_execute','stockholder_change_execute'
                ]
    execute_d = ['c_mortgage_execute', 's_creditor_execute',
                 'mortgage_execute'
                 ]

    cookies = response.cookies
    business = BusinessInfo1(link, cookies)  # 用link这个url进行实例化
    for c in executeA:
        print "%s %s %s" % ("*" * 20, c, "*" * 20)
        getattr(business, c)(pageSoup)
        if '已吊销' in business.qyxx_basicinfo[0]['check_type']:
            break


    # 动产抵押详情
    L = business.qyxx_mortgage_basic

    # 此处声明的三个变量是用于当有多个动产抵押项目的时候能把三个表的结果放到一个列表里面
    if L != []:
        headers = {
            'Host':'www.szcredit.com.cn',
            'Referer': link,
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/54.0.2840.71 Safari/537.36'
        }
        for dict in L:
            url = dict['detail'].split('>>>')[1]

            html = url_requests.get(url,
                                    headers = headers,
                                    cookies=response.cookies).text

            pageSoup = BeautifulSoup(html, 'lxml')

            for c in execute_d:
                print "%s %s %s" % ("*" * 20, c, "*" * 20)
                getattr(business, c)(pageSoup)

    results = business.returnData()

    return results

def main(**kwargs):

    link = kwargs.get('id_tag')

    if 'szcredit' in link:

        results = shenzhen(id_tag=link)
    else:
        results = guangdong(id_tag=link)

    return results

if __name__ == '__main__':

    # # 海丰县星云海实业有限公司（变更暂无数据）
    # link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_TnEJ0BpfDqRAyhTdKl4uIIAXqdMw9/aCoD' \
    #        '+IIPPiyrVTAOYLpc4gxgb5a3wjX8k3-Zr9d33V8OP2JUkdg6s0GPA=='

    # 兴宁市中恒眼镜配件有限公司(变更有查看更多资料，经营异常，抽查)
    link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
           'service=entInfo_N36dYNuUTaB78O3n9De28Gg/Dgnzvw1Q' \
           '+YrGtoZi2XdTAOYLpc4gxgb5a3wjX8k3-tF6QxU8NH+larVWkm1M5Vg=='
    # link = u'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList' \
    #        u'.html?service=entInfo_VkIxhDv3HJWgJDW9' \
    #        u'+fYBYMLds7yjSeSDehQMg40wF1tTAOYLpc4gxgb5a3wjX8k3' \
    #        u'-JSq07N4GaQgAKfMaxjk1bA=='

    # # 广州腾讯科技有限公司
    # link = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_nPNw57QPCnL961TNeXO4Gqc/FgBy7ESTwWPrP4zJe5g' \
    #        '=-7PUW92vxF0RgKhiSE63aCw=='

    # # 佛山禅城杨文军拜顿口腔诊所（普通合伙）(变更信息翻页)
    # link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_AAWDmeGKjHIXEWfvGuCvy' \
    #        '+fLK5YiauVB1sM4NVQBugyiRNHVa3OjFjvFlE8BfrFb' \
    #        '-xT4RauWNHMXwitj3hLbtLg=='

    # # 东莞市友谊国际劳务有限公司
    # link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_Se30rZJVgWG459' \
    #        '/tKQrYrOUZCdj7G5CrbDs6WUvrvBmfmyhBDv7NveR1uYRpZWc' \
    #        '+-/XFgzpZhFmHglFuKNWonYg=='  # 股东信息多页

    # # 深圳市华星光电技术有限公司(动产抵押详情, 变更信息)
    # link = 'http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?' \
    #        'rid=8b6bc52967b24ca2bd64e24414bce059'

    # # 深圳市科腾讯原材料供应有限公司 (经营异常)
    # link = 'http://www.szcredit.com.cn/web/GSZJGSPT/QyxyDetail.aspx?' \
    #        'rid=c72b446fb83b473a89eca9f22a90af90'
    # link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_vDZo00k5TYnhXlFUSQuMUOy82H2oWwwT9JonaQ6dpSoaxbRP4S73JXqCQJVBFZtz-A4QQZ+x+p5w5+akWCcoRYQ=='
    # link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo_2AkJwyRwcjCsxKvFcsvxfQu7FuNweelTKqiEutOP+spTAOYLpc4gxgb5a3wjX8k3-d+JRT9PzZSpyNRXG+nYwnA=='

    main(id_tag=link)