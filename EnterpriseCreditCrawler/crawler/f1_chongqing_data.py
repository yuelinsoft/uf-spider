# -*- coding:utf-8 -*-

"""
    create in 2016-12-27

    @author: lijianbin
    重庆改版后, 历史脚本在history目录下。
"""

from __future__ import unicode_literals
import re
import time
import json
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo

def get_url(hyperlinks, search_params, keyword):
    """该函数绕了一个大弯来获取能最终获取数据的url地址

    1、（base64编码尾部）
    http://cq.gsxt.gov.cn/gscx/qylx/nzgsfr.html?cHJpcGlkPTUwMDEwMzAwMDAwMzA0MjImcHJpdHlwZT0xJmVuY3J5cHQ9MQ==
    2、
    http://cq.gsxt.gov.cn/gscx/yyzz/gtgsh_yyzzxx.html
    3、
    http://cq.gsxt.gov.cn/gsxt/api/ebaseinfo/querygtForm/@pripid/@pritype
    由1得到2,由2得到3。

    :param hyperlinks 这是main函数中获取到的超链接的集
    :param search_params 查询参数，此处是dict
    :param keyword 具体版块的名称的关键字list，如 营业执照，股东出资等关键字
    """


    hyperlink = ''
    for each in hyperlinks:
        title = each.previous_sibling.previous_sibling.string
        for each_key in keyword:
            if each_key in title:
                hyperlink = ('http://cq.gsxt.gov.cn/gscx' +
                             each['ng-include'][3:-1])
                break
        if hyperlink:
            break
    if hyperlink:
        response = url_requests.get(hyperlink)
        geturl = 'http://cq.gsxt.gov.cn/gsxt/api' + \
                 re.findall('geturl="(.*?)"', response.content, re.S)[0] \
                     .replace('@pripid', search_params['pripid']) \
                     .replace('@pritype', search_params['pritype'])
    else:
        geturl = ''

    return geturl


class Credit(CreditInfo):
    """继承信用信息类

    """

    def __init__(self, query):
        self.query = query
        self.mortgage_reg_num = None  # 存动产抵押登记编号
        self.headers = {

        'Host': 'cq.gsxt.gov.cn',
        'appkey': '8dc7959eeee2792ac2eebb490e60deed',
        'User-Agent': ('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                       'AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/55.0.2883.87 Safari/537.36'),
        'Referer': ('http://cq.gsxt.gov.cn/gscx/qylx/nzgsfr.html'
                    '?cHJpcGlkPTUwMDAwMDEyMDE0MDUyMTA1NDc2MjMmcHJpdHlwZT0x')
    }
        super(Credit, self).__init__() # 继承父类的__init__

    def basicinfo_execute(self, **kwargs):
        """营业执照信息"""
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['营业执照']
        geturl = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        response = url_requests.get(url=geturl,
                                    params=params,
                                    headers=self.headers,
                                    proxies=proxies)
        try:
            jsn = json.loads(response.content)
            basicinfo = jsn[0]['form']
        except:
            print response.content
            raise
        info = {}
        info['company_name'] = basicinfo.get('entname', basicinfo.get('traname', ''))
        info['reg_num'] = basicinfo.get('uniscid', '')
        info['owner'] = basicinfo.get('name', '')
        info['address'] = basicinfo.get('dom', basicinfo.get('oploc', ''))
        info['start_date'] = basicinfo.get('estdate', '')
        info['fund_cap'] = basicinfo.get('regcap', '')
        if info['fund_cap']:
            info['fund_cap'] = info['fund_cap'] + '(万%s)' % \
                                                  basicinfo.get('regcapcur_cn')
        info['company_type'] = basicinfo.get('enttype_cn', '')
        info['business_area'] = basicinfo.get('opscope', '')
        info['check_type'] = basicinfo.get('regstate_cn', '')
        info['authority'] = basicinfo.get('regorg_cn', '')
        info['check_date'] = basicinfo.get('apprdate', '')
        info['business_from'] = basicinfo.get('opfrom', '')
        info['locate'] = '重庆市'

        self.qyxx_basicinfo.append(info)

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, **kwargs):

        hyperlinks = kwargs.get('hyperlink')
        keyword = ['股东及出资']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise
            for each_item in items:
                item = {}
                item['s_h_name'] = each_item.get('inv', '')
                item['s_h_type'] = each_item.get('invtype_cn', '')
                item['s_h_id_type'] = each_item.get('blictype_cn', '')
                item['s_h_id'] = each_item.get('blicno', '')

                self.qyxx_s_h.append(item)

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['变更信息']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise
            for each_item in items:
                item = {}
                item['reason'] = each_item.get('altitem_cn', '')
                item['before_change'] = each_item.get('altbe', '')
                item['after_change'] = each_item.get('altaf', '')
                item['date_to_change'] = each_item.get('altdate', '')

                self.qyxx_b_c.append(item)

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, **kwargs):

        hyperlinks = kwargs.get('hyperlink')
        keyword = ['主要人员', '家庭成员']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']  # list, 一行一个元素
            except:
                print response.content
                raise

            for each_row in items:
                for each_person in each_row:
                    item = {}
                    item['person_name'] = each_person.get('name', '').strip()
                    item['p_position'] = each_person.get('position_cn',
                                                         '').strip()

                    self.qyxx_member.append(item)

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['分支机构']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise
            for each_row in items:
                for each_ent in each_row:
                    item = {}
                    item['company_num'] = each_ent.get('brid', '')
                    item['company_name'] = each_ent.get('brname', '')
                    item['authority'] = each_ent.get('regorg_cn', '')

                    self.qyxx_branch.append(item)

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['动产抵押']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise

            for each_item in items:
                item = {}
                item['mortgage_reg_num'] = each_item.get('morregcno', '')
                item['date_reg'] = each_item.get('regidate', '')
                item['authority'] = each_item.get('regorg_cn', '')
                item['amount'] = each_item.get('priclasecam', '') + '万元'
                item['status'] = each_item.get('type', '').replace('1', '有效')\
                                                          .replace('2', '无效')
                item['detail'] = each_item

                self.qyxx_mortgage_basic.append(item)

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['股权出资']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise
            for each_item in items:
                item = {}
                item['reg_code'] = each_item.get('equityno', '')
                item['pleder'] = each_item.get('pledgor', '')
                item['id_card'] = each_item.get('pledblicno', '')
                item['plede_amount'] = each_item.get('impam', '')
                item['brower'] = each_item.get('imporg', '')
                item['brower_id_card'] = each_item.get('imporgblicno', '')
                item['reg_date'] = each_item.get('equpledate', '')
                item['status'] = each_item.get('type_text', '')
                item['changes'] = '详情'

                self.qyxx_pledge.append(item)

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['行政处罚']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise
            for each_item in items:
                item = {}
                item['pun_number'] = each_item.get('pendecno', '')
                item['reason'] = each_item.get('illegacttype', '')
                item['fines'] = each_item.get('pencontent', '')
                item['authority'] = each_item.get('penauth_cn', '')
                item['pun_date'] = each_item.get('pendecissdate', '')
                item['gongshiriqi'] = each_item.get('publicdate', '')

                self.qyxx_adm_punishment.append(item)

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['经营异常']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise

            for each_item in items:
                item = {}
                item['reason'] = each_item.get('specause_cn', '')
                item['date_occurred'] = each_item.get('abntime', '')
                item['authority_in'] = each_item.get('decorg_cn', '')
                item['reason_out'] = each_item.get('remexcpres_cn', '')
                item['date_out'] = each_item.get('remdate', '')
                item['authority_out'] = each_item.get('redecorg_cn', '')

                if item['authority_out'] == '' and item['authority_in']:
                    item['authority'] = item.pop('authority_in')
                    item.pop('authority_out')
                else:
                    item['authority'] = item.pop('authority_out')
                    item.pop('authority_in')

                self.qyxx_abnormal.append(item)

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['严重违法']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise
            for each_item in items:
                item = {}
                item['reason_in'] = each_item.get('serillrea_cn', '')
                item['date_in'] = each_item.get('abntime', '')
                item['authority_in'] = each_item.get('decorg_cn', '')
                item['reason_out'] = each_item.get('remexcpres_cn', '')
                item['date_out'] = each_item.get('remdate', '')
                item['authority_out'] = each_item.get('recorg_cn', '')

                if item['authority_out'] == '' and item['authority_in']:
                    item['authority'] = item.pop('authority_in')
                    item.pop('authority_out')
                else:
                    item['authority'] = item.pop('authority_out')
                    item.pop('authority_in')

                self.qyxx_black_info.append(item)

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['抽查检查']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise

            for each_item in items:
                item = {}
                item['authority'] = each_item.get('insauth_cn', '')
                item['spot_type'] = each_item.get('instype', '')
                item['spot_date'] = each_item.get('insdate', '')
                item['spot_result'] = each_item.get('insres_cn', '')

                self.qyxx_spot_check.append(item)

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, **kwargs):
        hyperlinks = kwargs.get('hyperlink')
        keyword = ['司法协助']
        url = get_url(hyperlinks, self.query, keyword)

        params = kwargs.get('params')
        if url:
            response = url_requests.get(url=url,
                                        params=params,
                                        headers=self.headers,
                                        proxies=proxies)
            try:
                jsn = json.loads(response.content)
                items = jsn[0]['list']
            except:
                print response.content
                raise

            for each_item in items:
                item = {}
                item['person'] = each_item.get('inv', '')
                item['stock'] = each_item.get('infroam', each_item.get(
                                                                'froam', ''))
                item['court'] = each_item.get('froauth', '')
                item['notice_number'] = each_item.get('executeno', '')
                item['status'] = each_item.get('frozstate_cn', '')

                self.qyxx_stock_freeze.append(item)

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, **kwargs):
        """表头结构已经变化"""
        # url = ('http://cq.gsxt.gov.cn/gsxt/api/ebaseinfo/queryForm'
        #        '/%s/1' % self.id)
        #
        # params = kwargs.get('params')
        #
        # response = url_requests.get(url=url,
        #                             params=params,
        #                             headers=self.headers,
        #                             proxies=proxies)
        # key_list = ['xuhao','person','stock','person_get','court','detail']

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, **kwargs):

        mort_id = kwargs.get('mort_id')
        url = ('http://cq.gsxt.gov.cn/gsxt/api/mortreginfo/dcdy'
               '/%s' % mort_id)

        params = kwargs.get('params')

        response = url_requests.get(url=url,
                                    params=params,
                                    headers=self.headers,
                                    proxies=proxies)
        try:
            jsn = json.loads(response.content)
            info = jsn[0]['form']
        except:
            print response.content
            raise
        item = {}
        item['mortgage_reg_num'] = info.get('morregcno', '')
        self.mortgage_reg_num = info.get('morregcno', '')
        item['date_reg'] = info.get('regidate', '')
        item['authority'] = info.get('regorg_cn', '')
        item['mortgage_type'] = ''
        item['amount'] = ''
        item['time_range'] = ''
        item['mortgage_range'] = ''

        self.qyxx_c_mortgage.append(item)

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, **kwargs):

        mort_id = kwargs.get('mort_id')
        url = ('http://cq.gsxt.gov.cn/gsxt/api/mortprincipalclaim/dcdydb'
               '/%s' % mort_id)

        params = kwargs.get('params')

        response = url_requests.get(url=url,
                                    params=params,
                                    headers=self.headers,
                                    proxies=proxies)
        try:
            jsn = json.loads(response.content)
            info = jsn[0]['form']
        except:
            print response.content
            raise
        item = {}
        item['mortgage_reg_num'] = self.mortgage_reg_num
        item['mortgage_type'] = info.get('priclaseckind_cn', '')
        item['amount'] = info.get('priclasecam', '') + '万元'
        item['mortgage_range'] = info.get('warcov', '')
        item['time_range'] = info.get('pefperform', '') + '至' + info.get(
                                        'pefperto', '')

        self.qyxx_s_creditor.append(item)

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, **kwargs):

        mort_id = kwargs.get('mort_id')
        url = ('http://cq.gsxt.gov.cn/gsxt/api/mortguarantee/queryList'
               '/%s' % mort_id)

        params = kwargs.get('params')

        response = url_requests.get(url=url,
                                    params=params,
                                    headers=self.headers,
                                    proxies=proxies)
        try:
            jsn = json.loads(response.content)
            items = jsn[0]['list']
        except:
            print response.content
            raise
        item_list = []
        for each_item in items:
            item = {}
            item['mortgage_reg_num'] = self.mortgage_reg_num
            item['mortgage_name'] = each_item.get('guaname', '')
            item['belongs'] = each_item.get('own', '')
            item['information'] = each_item.get('guades', '')
            item['mortgage_range'] = each_item.get('remark', '')

            item_list.append(item)

        self.qyxx_mortgage.extend(item_list)


def main(**kwargs):
    """数据解析流程

    目前只需要pripid这个参数，为防止后期需要更多的参数，所以将整个query返回的字典传过来。
    """

    search_data = kwargs.get('id_tag')    # query拿到的结果是dict
    global proxies
    proxies = kwargs.get('proxies')

    # 找到可以返回各个板块数据的网址
    pubtype = search_data.get('pubtype')
    host_url = 'http://cq.gsxt.gov.cn/gscx/qylx/%s.html?' % pubtype
    key = 'pripid=%s&pritype=%s&encrypt=1' % (search_data.get('pripid'),
                                              search_data.get('pritype'))
    # a = base64.b64encode(key.decode('utf-8').encode('gbk'))
    url = host_url + key
    response = url_requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    # 打印企业类型
    print soup.title.text
    hyperlink = soup.find_all('div', {'ng-show':'true'})

    # 不同的板块，不同的请求。返回的是json，因此不需要作外部请求，直接实例化执行每个方法即可。
    all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute', 'member_execute',
        'branch_execute', 'mortgage_basic_execute', 'pledge_execute',
        'adm_punishment_execute', 'abnormal_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

    # 实例化
    credit = Credit(query=search_data)

    # 通用网址后缀，即params参数。
    params = {
        'currentpage': 1,
        'pagesize': 100,  # 设置尽可能大的值是为了将数据一次性返回
        't': int(time.time() * 1000)
    }

    for each in all_execute[:-3]:
        print "Executing: %s" % each    # 依次执行每一个板块的方法
        getattr(credit, each)(params=params, hyperlink=hyperlink)

    # 若存在动产抵押信息，则执行下文，若无，则不执行，不影响数据返回格式。
    if credit.qyxx_mortgage_basic:
        for each_mort in credit.qyxx_mortgage_basic:
            mort_id = each_mort['detail']['morreg_id']
            for each in all_execute[-3:]:
                print "Executing: %s" % each
                getattr(credit, each)(params=params, mort_id=mort_id)

    results = credit.returnData()

    return results

if __name__ == '__main__':

    # # 重庆惠民金融服务有限责任公司(基本信息，股东信息，主要人员，变更信息-翻页)
    # id = '5000001201405210547623'
    #
    # # 重庆好士通房地产经纪有限公司(经营异常)
    # id = '500108010100016788'

    # # 重庆桃花源山泉水有限公司(抽查检查)
    # id = '5002341201504070946773'

    # # 重庆学府医院投资管理有限公司(股权出资登记)
    # id = '500902010100004834'

    # 梁平县品之山农牧科技有限公司(分支机构，动产抵押，股权出质)
    id = '500228010100005673'

    # # 南川区时尚通讯门市部（行政处罚）
    # id = '5003840000122933'

    # # 重庆康碧特食品有限公司(股东冻结)
    # id = '500237010100004493'
    query = {
        'pritype':'5',
        'isillegal':'',
        'entname':'<B>璧</B><B>山</B><B>区</B><B>香</B><B>熹</B><B>庄</B><B>食品</B><B>经</B><B>营</B><B>部</B>',
        'isabnormal':'',
        'regno_title':'500227605551745',
        'enttype':'9999',
        'uniscid_title':'',
        'regstate_cn':'存续',
        'entnameHL':'璧山区香熹庄食品经营部',
        'rnocurr':'1548942',
        'regcap':'0',
        'pubtype':'gtgsh',
        'score':'NaN',
        'regno':'500227605551745',
        'pripid':'5002271201505181011651',
        'estdate':'2015年05月18日',
        'uniscid':'',
        'regstate':'1',
        'name_title':'经营者',
        'name':'周强'
    }
    main(id_tag=query)