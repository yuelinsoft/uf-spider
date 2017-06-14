# -*- coding:utf-8 -*-
"""
    __author__ = 'lijianbin'

    该脚本用于抓取广州企业信用信息
"""

from __future__ import unicode_literals
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common.uf_exception import (RequestError)

class BusinessInfo(CreditInfo):
    """工商公示信息类"""

    def __init__(self, cookies):
        super(BusinessInfo, self).__init__()

        self.headers = {
                'Host': 'gsxt.gzaic.gov.cn',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
                'Referer': 'http://gsxt.gzaic.gov.cn/aiccips/CheckEntContext/showInfo.html'
            }
        self.cookies = cookies
        self.mortgage_reg_num = None

    # 登记信息部分
    def basicinfo_execute(self, data):
        '''
        :return: 基本信息 dict
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo'
        response = url_requests.post(url, headers=self.headers, data=data, cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('table', {'id': 'baseinfo'})
        if soup == None:
            raise RequestError("没有查询到企业的相关信息，应该是访问出错了。")

        Info = self.parse(soup, 'table', {'id': 'baseinfo'})

        if Info:
            if Info[0].has_key('统一社会信用代码') and Info[0].has_key('注册号'):
                if Info[0]['统一社会信用代码'] == '':
                    Info[0]['统一社会信用代码'] = Info[0]['注册号']

            Info[0] = common.basicinfo_dict(Info[0], '广州市')

            self.qyxx_basicinfo = Info

    # 股东信息
    def s_h_execute(self, data):
        '''

        :param data: 包含企业id的query文件中返回的data
        :return:
        '''

        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('div', {'id': 'invInfo'})
        key_list = ['s_h_type', 's_h_name', 's_h_id_type', 's_h_id',
                    'xiangqing']
        # key_list = ['股东类型', '股东', '股东证件类型', '股东证件号', 详情]
        self.qyxx_s_h = self.parse(soup, 'div', {'id': 'invInfo'},
                                 key_list=key_list)

    # 变更信息
    def b_c_execute(self, data):
        '''
        :return: 变更信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('div', {'id': 'biangeng'})
        key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        self.qyxx_b_c = self.parse(soup, 'div', {'id': 'biangeng'},
                             key_list=key_list)

    # 备案信息——主要成员信息
    def member_execute(self, data):
        '''
        :return: 主要成员信息 list, 是 [姓名，职位] 列表
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entCheckInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('div', {'id': 'zyry'})
        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']

        self.qyxx_member = self.parse(soup, 'div', {'id': 'zyry'}, key_list=key_list)

    # 备案信息——分支机构信息
    def branch_execute(self, data):
        '''
        :return: 分支机构信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=entCheckInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        self.qyxx_branch = self.parse(soup, 'div', {'id': 'branch'},
                               key_list=key_list)

    # 动产抵押登记
    def mortgage_basic_execute(self, data):
        '''
        :return: 动产抵押登记信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=pleInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        # soup = soup.find('div', {'id': 'branch'})
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority', 'amount', 'status', 'detail']
        # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'详情']
        self.qyxx_mortgage_basic = self.parse(soup, key_list=key_list)

    # 股权出资登记信息
    def pledge_execute(self, data):
        '''
        :return: 股权出资登记信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=curStoPleInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '变化情况']

        self.qyxx_pledge = self.parse(soup, key_list=key_list)


    # # 行政处罚信息
    def adm_punishment_execute(self, data):
        '''
        :return: 行政处罚信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=cipPenaltyInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority', 'pun_date', 'xiangqing']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','详情']
        self.qyxx_adm_punishment = self.parse(soup, key_list=key_list)


    # 经营异常信息
    def abnormal_execute(self, data):
        '''
        :return: 经营异常信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=cipUnuDirInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'reason', 'date_occurred', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '移出异常原因', '移出日期', '作出决定机关（列出）']

        self.qyxx_abnormal = self.parse(soup, key_list=key_list)

    # 严重违法信息
    def black_info_execute(self, data):
        '''
        :return: 严重违法信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=cipBlackInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'reason_in', 'date_in', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']

        self.qyxx_black_info = self.parse(soup, key_list=key_list)

    # 抽查检查信息
    def spot_check_execute(self, data):
        '''
        :return: 抽查检查信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?service=cipSpotCheInfo'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date', 'spot_result']
        # key_list = ['序号','检查实施机关','类型','日期','结果']

        self.qyxx_spot_check = self.parse(soup, key_list=key_list)

    # 股权冻结信息
    def stock_freeze_execute(self, data):
        '''
        :return:
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/judiciaryAssist/judiciaryAssistInit.html '
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number', 'status', 'xiangqing']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']

        self.qyxx_stock_freeze = self.parse(soup, key_list=key_list)

    # 股东变更信息
    def stockholder_change_execute(self, data):
        '''
        :return: 司法股东变更登记信息 or 行政处罚信息
        '''
        url = 'http://gsxt.gzaic.gov.cn/aiccips/sfGuQuanChange/guQuanChange.html'
        response = url_requests.post(url, headers=self.headers, data=data,
                                     cookies=self.cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        key_list = ['xuhao', 'person', 'stock', 'person_get', 'court', 'xiangqing']
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

def main(**kwargs):

    link = kwargs.get('id_tag')

    # 先访问query脚本返回的url获取其中的三个参数entNo， entType， regOrg，并组成data用于访问每个模块。
    headers = {
        'Host': 'gsxt.gzaic.gov.cn',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36',
        'Referer': 'http://gsxt.gdgs.gov.cn/aiccips/main/initJyycInfoList.html'
    }

    response = url_requests.get(link, headers=headers, timeout=10)
    cookies = response.cookies
    # print cookies
    soup = BeautifulSoup(response.text, 'lxml')
    req_data = {}
    req_data['entNo'] = soup.find('input', {'name': 'entNo'})['value']
    req_data['entType'] = soup.find('input', {'name': 'entType'})['value']
    req_data['regOrg'] = soup.find('input', {'name': 'regOrg'})['value']

    # 接着用这个req_data作为参数，传给每一个模块的url，获取信息。
    executeA = ['basicinfo_execute', 'abnormal_execute', 'adm_punishment_execute', 'b_c_execute',
                'branch_execute', 'member_execute', 'mortgage_basic_execute', 'pledge_execute',
                's_h_execute', 'spot_check_execute', 'black_info_execute', 'stock_freeze_execute', 'stockholder_change_execute']

    execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']

    businessInfo = BusinessInfo(cookies)
    loop = True     # 判断一次是否吊销，已吊销，则loop=False
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
    """暂未发现动产抵押企业"""
    if businessInfo.qyxx_mortgage_basic:
        # L = _result['qyxx_mortgage_basic']
        L = businessInfo.qyxx_mortgage_basic
        headers = {
            'Host': 'gsxt.gzaic.gov.cn',
            'Referer': 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity'
                       '/GSpublicityList.html?service=pleInfo',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/54.0.2840.71 Safari/537.36'
        }
        url = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList' \
              '.html'
        for dict in L:
            req_data['service'] = 'pleInfoData'
            req_data['pleNo'] = dict['detail'].split("'")[1]

            html = url_requests.get(url,
                                    params=req_data,
                                    headers=headers,
                                    cookies=response.cookies).text

            pageSoup = BeautifulSoup(html, 'lxml')

            pageSoup = pageSoup.find('div', {'id': 'details'})

            for c in execute_d:
                print "%s %s %s" % ("*" * 20, c, "*" * 20)
                getattr(businessInfo, c)(pageSoup)

    # 汇总数据到字典
    results = businessInfo.returnData()

    return results

if __name__ == '__main__':
    # link = 'http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_TnEJ0BpfDqRAyhTdKl4uIIAXqdMw9/aCoD+IIPPiyrVTAOYLpc4gxgb5a3wjX8k3-Zr9d33V8OP2JUkdg6s0GPA=='  # 海丰县星云海实业有限公司（变更暂无数据）
    link = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
           'service=entInfo_MI+0bthfTM6D5gR8OgV9SmAMeL+QrfB16FAzVlID1ZQ' \
           '=-50aS1uze1DaXd8Gk5PFw0A=='
    # link = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList.html?' \
    #        'service=entInfo_nPNw57QPCnL961TNeXO4Gqc/FgBy7ESTwWPrP4zJe5g=-7PUW92vxF0RgKhiSE63aCw=='  # 广州腾讯科技有限公司
    link = 'http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList' \
           '.html?service=entInfo_YvWpowOY6ROGm9xR7VBogxxyGFLQnM5pGHwJmlAumXI=-vDx4C5rJxvW+ZVXMJ+PbWg=='

    main(id_tag=link)