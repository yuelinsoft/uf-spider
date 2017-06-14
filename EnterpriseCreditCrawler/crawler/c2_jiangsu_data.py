# -*- coding: utf-8 -*-
"""
    Create in 2016.11.22

    __author__ = "lijianbin"

    江苏省网址第一次更改的版本, 每个独立的模块需要单独访问独立的网址，
    因此，16个表要访问16个网址。
    其中：基本信息、主要人员、分支机构属于get请求，
    其余为post请求，

    阅读代码及修改bug时应同时进行网页分析，注意字段名称的变化。
"""


from __future__ import unicode_literals
import json
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo
from EnterpriseCreditCrawler.common.uf_exception import UfException



class CompanyInfo(CreditInfo):
    """继承信用信息类

    """


    def __init__(self, item):
        """item是query获取到的items里的元素，包含了必要的查询字段。

        :param item: dict
        """

        super(CompanyInfo, self).__init__() # 继承父类的__init__
        self.mortgage_reg_num = None    # 存动产抵押登记编号

        self.headers = {
            'Host': 'www.jsgsj.gov.cn:58888',
            'X-Forwarded-For': '8.8.8.8',
            'Referer': ('http://www.jsgsj.gov.cn:58888/ecipplatform/jiangsu'
                        '.jsp'),
            'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/44.0.2403.155 Safari/537.36')
        }

        # 构造self.post_data字典，用于访问需要post请求的模块
        self.post_data = {
            'org': item.get('ORG'),
            'id': item.get('ID'),
            'seqId': item.get('SEQ_ID'),
            'abnormal': '',
            'activeTabId': '',
            'tmp': '',
            'regNo': '',
            'admitMain': '',
            'pageSize': 5,
            'curPage': 1,
            'sortName': '',
            'sortOrder': '',
            'uniScid': ''
        }

        # 构造self.params字典，用于访问需要get请求的模块
        self.params = {
            'org': item.get('ORG'),
            'id': item.get('ID'),
            'seqId': item.get('SEQ_ID'),
            'abnormal':	'',
            'activeTabId': '',
            'tmp': '',
            'regNo': '',
            'admitMain': '',
            'uniScid': ''
        }

# 注意：regNo的值需要在执行了basicinfo后获得，因此，basicinfo_execute方法必须第一个执行

    def basicinfo_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json')

        self.params['pageView'] = 'true'

        resp = url_requests.get(url=url,
                                params=self.params,
                                headers=self.headers,
                                proxies=proxies)
        data = json.loads(resp.content)

        # 将所需要的信息保存在对应的属性里
        info = {
            'company_name': data.get('CORP_NAME', ''),
            'fund_cap': data.get('REG_CAPI', ''),
            'company_type': data.get('ZJ_ECON_KIND', ''),
            'check_type': data.get('CORP_STATUS', ''),
            'authority': data.get('BELONG_ORG', ''),
            'check_date': data.get('CHECK_DATE', ''),
            'locate': '江苏省',
            'owner': data.get('OPER_MAN_NAME', ''),
            'address': data.get('ADDR', ''),
            'reg_num': data.get('REG_NO', ''),
            'business_area': data.get('FARE_SCOPE', ''),
            'start_date': data.get('START_DATE', ''),
            'business_from': data.get('FARE_TERM_START', ''),
            '营业期限至': data.get('FARE_TERM_END', '')
        }
        self.qyxx_basicinfo.append(info)
# 注意：执行完后，要为self.params和self.post_data的regNo赋值
        self.params['regNo'] = data.get('REG_NO_EN')
        self.params['admitMain'] = data.get('ADMIT_MAIN')
        self.params['uniScid'] = data.get('UNI_SCID')
        self.post_data['regNo'] = data.get('REG_NO_EN')
        self.post_data['admitMain'] = data.get('ADMIT_MAIN')
        self.post_data['uniScid'] = data.get('UNI_SCID')

        self.params.pop('pageView')     # 执行完之后，删除该key值，以免影响其他模块

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryGdcz=true')

        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data') # list
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type']
        # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型']
        for each_data in data:
            info = {}
            info['s_h_name'] = each_data.get('STOCK_NAME', '')
            info['s_h_id_type'] = each_data.get('IDENT_TYPE_NAME', '')
            info['s_h_id'] = each_data.get('IDENT_NO', '')
            info['s_h_type'] = each_data.get('STOCK_TYPE', '')
            self.qyxx_s_h.append(info)

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryBgxx=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['reason', 'before_change', 'after_change',
                    'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        for each_data in data:
            info = {}
            info['reason'] = each_data.get('CHANGE_ITEM_NAME', '')
            info['before_change'] = each_data.get('OLD_CONTENT', '')
            info['after_change'] = each_data.get('NEW_CONTENT', '')
            info['date_to_change'] = each_data.get('CHANGE_DATE', '')
            self.qyxx_b_c.append(info)

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json')
        self.params['queryZyry'] = 'true'

        resp = url_requests.get(url=url,
                                params=self.params,
                                headers=self.headers,
                                proxies=proxies)
        data = json.loads(resp.content)
        key_list = ['person_name', 'p_position']
        # key_list = ['姓名', '职位']
        for each_data in data:
            info = {}
            info['person_name'] = each_data.get('PERSON_NAME', '')
            info['p_position'] = each_data.get('POSITION_NAME', '')
            self.qyxx_member.append(info)

        self.params.pop('queryZyry')    # 执行完之后，删除该key值，以免影响其他模块

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json')
        self.params['queryFzjg'] = 'true'

        resp = url_requests.get(url=url,
                                params=self.params,
                                headers=self.headers,
                                proxies=proxies)
        data = json.loads(resp.content)
        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        for each_data in data:
            info = {}
            info['company_num'] = each_data.get('DIST_REG_NO', '')
            info['company_name'] = each_data.get('DIST_NAME', '')
            info['authority'] = each_data.get('DIST_BELONG_ORG', '')
            self.qyxx_branch.append(info)

        self.params.pop('queryFzjg')    # 执行完之后，删除该key值，以免影响其他模块

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryDcdy=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['mortgage_reg_num', 'date_reg', 'authority',
                    'amount', 'status', 'details']
        # key_list = ['登记编号','登记日期','登记机关','被担保债权数额','状态','详情']
        for each_data in data:
            info = {}
            info['mortgage_reg_num'] = each_data.get('GUARANTY_REG_NO', '')
            info['date_reg'] = each_data.get('START_DATE', '')
            info['authority'] = each_data.get('CREATE_ORG', '')
            info['amount'] = each_data.get('ASSURE_CAPI', '')
            info['status'] = each_data.get('STATUS', '')
            info['details'] = each_data
            self.qyxx_mortgage_basic.append(info)

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryGqcz=true')

        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount',
                    'brower','brower_id_card', 'reg_date', 'status',
                    'publicity_date', 'changes']
        # key_list = ['登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '公式日期','变化情况']
        for each_data in data:
            string = each_data.get('D1')
            if string:
                soup = BeautifulSoup(string, 'lxml')
                values = soup.find_all('td', class_='lineWrap')
                info = {}
                for i, key in enumerate(key_list):
                    info[key] = values[i].text.strip()
                self.qyxx_pledge.append(info)

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryXzcf=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['pun_number', 'reason', 'fines', 'authority', 'pun_date']
        # key_list = ['行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期']
        for each_data in data:
            info = {}
            info['pun_number'] = each_data.get('PEN_DEC_NO', '')
            info['reason'] = each_data.get('ILLEG_ACT_TYPE', '')
            info['fines'] = each_data.get('PEN_TYPE', '')
            info['authority'] = each_data.get('PUNISH_ORG_NAME', '')
            info['pun_date'] = each_data.get('PUNISH_DATE', '')
            self.qyxx_adm_punishment.append(info)

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryJyyc=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['xuhao', 'reason', 'date_occurred', 'juedinglierujiguan',
                    'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '作出决定机关（列入）', '移出异常原因', '移出日期', '作出决定机关（列出）']
        for each_data in data:
            info = {}
            info['xuhao'] = each_data.get('RN', '')
            info['reason'] = each_data.get('FACT_REASON', '')
            info['date_occurred'] = each_data.get('MARK_DATE', '')
            info['juedinglierujiguan'] = each_data.get('CREATE_ORG', '')
            info['reason_out'] = each_data.get('REMOVE_REASON', '')
            info['date_out'] = each_data.get('CREATE_DATE', '')
            info['authority'] = each_data.get('YICHU_ORG', '')
            self.qyxx_abnormal.append(info)

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryYzwf=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['reason_in', 'date_in', 'authority_in',
                    'reason_out', 'date_out', 'authority']
        # key_list = ['登记编号','登记日期','登记机关','被担保债权数额','状态','详情']
        for each_data in data:
            info = {}
            info['reason_in'] = each_data.get('FACT_REASON', '')
            info['date_in'] = each_data.get('MARK_DATE', '')
            info['authority_in'] = each_data.get('MARK_ORG', '')
            info['reason_out'] = each_data.get('REMOVE_DATE', '')
            info['date_out'] = each_data.get('REMOVE_DATE', '')
            info['authority'] = each_data.get('REMOVE_ORG', '')
            self.qyxx_black_info.append(info)

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?queryCcjc=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['authority', 'spot_type', 'spot_date', 'spot_result']
        # key_list = ['检查实施机关','类型','日期','结果']
        for each_data in data:
            info = {}
            info['authority'] = each_data.get('CHECK_ORG', '')
            info['spot_type'] = each_data.get('CHECK_TYPE', '')
            info['spot_date'] = each_data.get('CHECK_DATE', '')
            info['spot_result'] = each_data.get('CHECK_RESULT', '')
            self.qyxx_spot_check.append(info)

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self):
        url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
               '/publicInfoQueryServlet.json?querySfxz=true')
        resp = url_requests.post(url=url,
                                 data=self.post_data,
                                 headers=self.headers,
                                 proxies=proxies)
        data = json.loads(resp.content)
        data = data.get('data')  # list
        key_list = ['person', 'stock', 'court', 'notice_number',
                    'status', 'details']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']

        for each_data in data:
            info = {}
            info['person'] = each_data.get('ASSIST_NAME', '')
            info['stock'] = each_data.get('FREEZE_AMOUNT', '')
            info['court'] = each_data.get('EXECUTE_COURT', '')
            info['notice_number'] = each_data.get('NOTICE_NO', '')
            info['status'] = each_data.get('FREEZE_STATUS', '')
            info['details'] = each_data                 # 带有访问详情所需的参数
            self.qyxx_stock_freeze.append(info)

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self):
        '''字段信息已经改变，原来的表结构已经不能反映现在的情况了。'''
        # url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
        #        '/publicInfoQueryServlet.json?queryQyjsxxGqbg=true')
        # resp = url_requests.post(url=url,
        #                          data=self.post_data,
        #                          headers=self.headers,
        #                          proxies=proxies)
        # data = json.loads(resp.content)
        # data = data.get('data')  # list
        #
        # if data:
        #     raise UfException("discover stockholder_change")

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self):
        if self.qyxx_mortgage_basic:
            url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
                   '/publicInfoQueryServlet.json?queryDcdyDetail=true')

            for each_mortgage in self.qyxx_mortgage_basic:
                data = {}
                data['org'] = each_mortgage['details']['ORG']
                data['id'] = each_mortgage['details']['ID']
                data['seqId'] = each_mortgage['details']['SEQ_ID']

                resp = url_requests.post(url=url,
                                         data=data,
                                         headers=self.headers,
                                         proxies=proxies)

                items = json.loads(resp.content)[0] # 数据中第二个是空字典
                info = {}
                info['mortgage_reg_num'] = items.get('GUARANTY_REG_NO', '')
                info['mortgage_type'] = items.get('ASSURE_KIND', '')
                info['amount'] = items.get('ASSURE_CAPI', '')
                info['time_range'] = items.get('ASSURE_START_DATE', '')
                info['mortgage_range'] = items.get('ASSURE_SCOPE', '')

                # 先获取被担保债权，再添加两个key就是基本登记信息
                self.qyxx_s_creditor.append(info)

                info['date_reg'] = items.get('START_DATE', '')
                info['authority'] = items.get('CREATE_ORG', '')

                # 再获取登记信息
                self.qyxx_c_mortgage.append(info)

                self.mortgage_reg_num = items.get('GUARANTY_REG_NO', '')

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self):
        print '被担保债权概况在登记信息中获得。'

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self):

        if self.qyxx_mortgage_basic:
            url = ('http://www.jsgsj.gov.cn:58888/ecipplatform'
                   '/publicInfoQueryServlet.json?queryDcdyDywgk=true')

            key_list = ['mortgage_name', 'belongs', 'information',
                        'mortgage_range']
            # key_list = ['抵押物名称', '所有权归属', '数量、质量等信息', '备注']

            for each_mortgage in self.qyxx_mortgage_basic:
                data = {}
                data['org'] = each_mortgage['details']['ORG']
                data['id'] = each_mortgage['details']['ID']
                data['seqId'] = each_mortgage['details']['SEQ_ID']
                data['pageSize'] = 0
                data['curPage'] = 1

                resp = url_requests.post(url=url,
                                         data=data,
                                         headers=self.headers,
                                         proxies=proxies)
                items = json.loads(resp.content)
                items = items.get('data')   # list
                mortgage_list = []
                for each in items:
                    info = {}
                    info['mortgage_name'] = each.get('NAME', '')
                    info['belongs'] = each.get('BELONG_KIND', '')
                    info['information'] = each.get('PA_DETAIL', '')
                    info['mortgage_range'] = each.get('REMARK', '')   # 备注
                    info['mortgage_reg_num'] = self.mortgage_reg_num
                    mortgage_list.append(info)
                self.qyxx_mortgage.extend(mortgage_list)

def main(**kwargs):
    items = kwargs.get('id_tag')
    global proxies
    proxies = kwargs.get('proxies')
    # proxies = None  # 暂时不使用代理IP

    all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute','member_execute',
        'branch_execute', 'adm_punishment_execute', 'abnormal_execute',
        'mortgage_basic_execute', 'pledge_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

    credit = CompanyInfo(items)
    loop = True  # 判断一次是否吊销，已吊销，则loop=False
    active = True  # 默认未吊销
    for each in all_execute:
        print "%s %s %s" % ("*" * 20, each, "*" * 20)
        getattr(credit, each)()
        # businessInfo.pledge_execute()
        if credit.qyxx_basicinfo:
            while loop:
                loop = False
                if '已吊销' in credit.qyxx_basicinfo[0]['check_type']:
                    active = False
        if not active:
            break
    results = credit.returnData()

    return results

if __name__ == '__main__':

    data = [
        {
            u'ABNORMAL': u'',
             u'SHOW_DATE': u'1997-07-28',
             u'CORP_STATUS': u'在业',
             u'REG_NO_CLM': u'统一社会信用代码/注册号',
             u'SEQ_ID': u'4C74D2EC475C412F8F40A90534A24FEC',
             u'REG_NO': u'91320282628411980H',
             u'ADMIT_MAIN': u'08',
             u'UNI_SCID': u'320282000077425',
             u'START_DATE': u'1997-07-28',
             u'OPER_MAN_NAME': u'陈建伟',
             u'ECON_KIND': 51,
             u'OPER_MAN_CLM': u'法定代表人',
             u'CORP_NAME': u'江苏省伟宇塑业有限公司',
             u'WRITEOFF_DATE': u'',
             u'CORP_NAME_LENGTH': 11,
             u'BELONG_ORG': u'宜兴市市场监督管理局',
             u'ORG': u'D6CAA68850078FCCB00B65D52F4FF48E',
             u'CORP_STATUS1': u'01',
             u'DATE_NAME_CLM': u'成立日期',
             u'ID': u'5F63D4E6B96A5920B8271876DEE5FCFA',
             u'REVOKE_DATE': u''
        },
        {
            'REG_NO_CLM': '统一社会信用代码/注册号',
            'REG_NO': '9132062313867696XG',
            'SHOW_DATE': '1990-03-07',
            'OPER_MAN_NAME': '吴建华',
            'BELONG_ORG': '如东县市场监督管理局',
            'DATE_NAME_CLM': '成立日期',
            'UNI_SCID': '320623000113839',
            'KEY_WORD_INDEX': '0',
            'CORP_STATUS1': '01',
            'REG_CAPI': '1940',
            'REVOKE_DATE': '',
            'SEQ_ID': 'D8DA35AFC946873A7AE974A8F25D8A09',
            'ABNORMAL': '',
            'OPER_MAN_CLM': '法定代表人',
            'ID': '19A83FB296C1BF2D84EA83E4CD025E48',
            'START_DATE': '1990-03-07',
            'CORP_STATUS': '在业',
            'WRITEOFF_DATE': '',
            'ECON_KIND': '51',
            'CORP_NAME': '如东纺织橡胶有限公司',
            'ADMIT_MAIN': '08',
            'ORG': 'DBBF2B3C27C5E35AC652C56F1A7BBB21'
            },
        {
            'REG_NO_CLM': '统一社会信用代码/注册号',
            'REG_NO': '320583000053818',
            'SHOW_DATE': '2002-08-07',
            'OPER_MAN_NAME': '蒋建初',
            'BELONG_ORG': '昆山市市场监督管理局',
            'DATE_NAME_CLM': '成立日期',
            'UNI_SCID': '',
            'KEY_WORD_INDEX': '0',
            'CORP_STATUS1': '01',
            'REG_CAPI': '1000',
            'REVOKE_DATE': '',
            'SEQ_ID': 'F6564ADAAE1E1CD03FF40E595DE88249',
            'ABNORMAL': '该企业被列入经营异常名录',
            'OPER_MAN_CLM': '法定代表人',
            'ID': 'BC62A79C5F53C206D24A11E8B12DD5B2',
            'START_DATE': '2002-08-07',
            'CORP_STATUS': '在业',
            'WRITEOFF_DATE': '',
            'ECON_KIND': '51',
            'CORP_NAME': '昆山中海工贸有限公司',
            'ADMIT_MAIN': '08',
            'ORG': '63D1B55F525DC58CC6E2E4C0113DB667'
        },
        {
            'REG_NO_CLM': '统一社会信用代码/注册号',
            'REG_NO': '913202823021404714',
            'SHOW_DATE': '2014-05-20',
            'OPER_MAN_NAME': '田卿',
            'BELONG_ORG': '宜兴市市场监督管理局',
            'DATE_NAME_CLM': '成立日期',
            'UNI_SCID': '320282000359348',
            'KEY_WORD_INDEX': '0',
            'CORP_STATUS1': '01',
            'REG_CAPI': '5000',
            'REVOKE_DATE': '',
            'SEQ_ID': '1B2020BCF7177FF66061F3F30FF996AF',
            'ABNORMAL': '',
            'OPER_MAN_CLM': '法定代表人',
            'ID': 'D8930397B66386D4FFC185041FF604B8',
            'START_DATE': '2014-05-20',
            'CORP_STATUS': '在业',
            'WRITEOFF_DATE': '',
            'ECON_KIND': '180',
            'CORP_NAME': '江苏文远生态农业科技有限公司',
            'ADMIT_MAIN': '08',
            'ORG': 'D6CAA68850078FCCB00B65D52F4FF48E'
         },
        {
            'REG_NO_CLM': '统一社会信用代码/注册号',
            'REG_NO': '91320000134770529W',
            'SHOW_DATE': '1993-05-28',
            'OPER_MAN_NAME': '余翔',
            'BELONG_ORG': '江苏省工商行政管理局',
            'DATE_NAME_CLM': '成立日期',
            'UNI_SCID': '320000000005718',
            'KEY_WORD_INDEX': '0',
            'CORP_STATUS1': '01',
            'REG_CAPI': '8000',
            'REVOKE_DATE': '',
            'SEQ_ID': 'A074379A22DBCE2DDE7614F45B911808',
            'ABNORMAL': '该企业被列入经营异常名录',
            'OPER_MAN_CLM': '法定代表人',
            'ID': 'D480590175C64F2AA44A4937056C4E92',
            'START_DATE': '1993-05-28',
            'CORP_STATUS': '在业',
            'WRITEOFF_DATE': '',
            'ECON_KIND': '181',
            'CORP_NAME': '江苏汇远房地产发展有限责任公司',
            'ADMIT_MAIN': '08',
            'ORG': '6983AED1959EFDD1779E9DBFB475D88C'
         },
        {
            'REG_NO_CLM': '统一社会信用代码/注册号',
            'REG_NO': '91320200060222553L',
            'SHOW_DATE': '2013-01-24',
            'OPER_MAN_NAME': '石井英雅',
            'BELONG_ORG': '无锡市工商行政管理局',
            'DATE_NAME_CLM': '成立日期',
            'UNI_SCID': '320200400037279',
            'KEY_WORD_INDEX': '0',
            'CORP_STATUS1': '01',
            'REG_CAPI': '13900',
            'REVOKE_DATE': '',
            'SEQ_ID': 'B171BF4CAE8495DAB40F01172054D8CB',
            'ABNORMAL': '',
            'OPER_MAN_CLM': '法定代表人',
            'ID': '020BE1098BB454931AF58AFE5D59C099',
            'START_DATE': '2013-01-24',
            'CORP_STATUS': '在业',
            'WRITEOFF_DATE': '',
            'ECON_KIND': '195',
            'CORP_NAME': '丸悦（无锡）商贸有限公司',
            'ADMIT_MAIN': '10',
            'ORG': 'D6CAA68850078FCCB00B65D52F4FF48E'
        }
    ]
    for i in data:
        print main(id_tag=i)
