# -*- coding:utf-8 -*-
"""
    @author: lijianbin

    改成滑快后的广东，可兼容广州，不兼容深圳
"""


from __future__ import unicode_literals
import time
import json
from bs4 import BeautifulSoup
from EnterpriseCreditCrawler.common import common
from EnterpriseCreditCrawler.common import url_requests
from EnterpriseCreditCrawler.common.page_parse import CreditInfo
from EnterpriseCreditCrawler.common.uf_exception import IpRefused

class Enterprise(CreditInfo):
    """继承信用信息类(模板)

    基本信息、主要人员、分支机构，这三个板块的data参数不需要key——pageNo
    其他出动产抵押的三个附表和以上三个板块都是不需要entType，而需要pageNo这个key。
    目前是都传递4个key，若日后出现问题，需要精准的传递data的key。
    """

    def __init__(self, **kwargs):
        super(Enterprise, self).__init__()  # 继承父类的__init__
        self.mortgage_reg_num = None  # 存动产抵押登记编号
        self.host = kwargs.get('host')
        self.data = kwargs.get('data')
        self.data['pageNo'] = 1
        self.headers = kwargs.get('headers')

    def basicinfo_execute(self):

        url = ('http://%s/aiccips/GSpublicity/GSpublicityList'
               '.html?service=entInfo') % self.host

        response = url_requests.post(url=url,
                                     data=self.data,
                                     headers=self.headers,
                                     proxies=proxies)
        soup = BeautifulSoup(response.text, 'lxml')

        self.soup = soup    # 赋值到属性，可获取营业执照、主要成员、分支机构三项信息

        body = soup.find('div', {'style':'padding-left: 14px'})
        info = {}
        labels = body.find_all('span', class_='label')
        for label in labels:
            key = label.text.replace('：', '').strip()
            value = label.next_sibling.text.strip()
            info[key] = value
        info = common.basicinfo_dict(info, '广东省')

        self.qyxx_basicinfo.append(info)

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self):

        url = ('http://%s/aiccips//invInfo/invInfoList' % self.host)
        response = url_requests.get(url=url,
                                     params=self.data,
                                     headers=self.headers,
                                     proxies=proxies)
        items = json.loads(response.text)['list']['list']   # type is list
        if items:
            for each_item in items:
                item = {}
                item['s_h_name'] = each_item.get('inv', '')
                item['s_h_type'] = each_item.get('invType', '')
                item['s_h_id_type'] = each_item.get('certName', '')
                if not item['s_h_id_type']:
                    item['s_h_id_type'] = '(非公示项)'

                item['s_h_id'] = each_item.get('certNo', '')
                if item['s_h_type'] == '自然人股东':
                    item['s_h_id'] = '(非公示项)'
                elif not item['s_h_id']:
                    item['s_h_id'] = ''

                self.qyxx_s_h.append(item)

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self):

        url = ('http://%s/aiccips//EntChaInfo/EntChatInfoList' % self.host)
        response = url_requests.get(url=url,
                                    params=self.data,
                                    headers=self.headers,
                                    proxies=proxies)
        items = json.loads(response.text)['list']['list']  # type is list
        if items:
            for each_item in items:
                item = {}
                item['reason'] = each_item.get('altFiledName', '')
                item['before_change'] = each_item.get('altBe', '')
                item['after_change'] = each_item.get('altAf', '')
                item['date_to_change'] = each_item.get('altDate', '')
                if item['date_to_change']:
                    # 将时间戳转换成日期
                    date = time.localtime(item['date_to_change'] / 1000)
                    item['date_to_change'] = time.strftime("%Y-%m-%d", date)

                self.qyxx_b_c.append(item)

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self):
        """"""

        url = ('http://%s/aiccips/GSpublicity/GSpublicityList.html?service'
               '=entInfo' % self.host)

        response = url_requests.post(url=url,
                                     data=self.data,
                                     headers=self.headers,
                                     proxies=proxies)
        soup = BeautifulSoup(response.text, 'lxml')
        tag = soup.find('div', {'id': 'braFlag'})
        if tag:
            tag = tag.previous_sibling.previous_sibling
            try:
                members = tag.find_all('td')
            except AttributeError:
                return []
            for member in members:
                if '暂无数据' in member.text:
                    return []
                info = {}
                key = member.find('span', class_='nameText').text.strip()
                value = member.find('span', class_='positionText').text.strip()
                info['person_name'] = key
                info['p_position'] = value

                self.qyxx_member.append(info)

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self):

        url = ('http://%s/aiccips/GSpublicity/GSpublicityList.html?service'
               '=entInfo' % self.host)

        response = url_requests.post(url=url,
                                     data=self.data,
                                     headers=self.headers,
                                     proxies=proxies)
        soup = BeautifulSoup(response.text, 'lxml')
        tag = soup.find('div', {'id': 'braFlag'})
        if tag:
            tag = tag.next_sibling.next_sibling
            try:
                branch = tag.find_all('td')
            except AttributeError:
                return []
            for each_ent in branch:
                if '暂无数据' in each_ent.text:
                    return []
                info = {}
                info['company_name'] = each_ent.find('span',
                                                 class_='conpany').text.strip()
                info['company_num'] = each_ent.find('span',
                                                 class_='textcor').text.strip()
                info['authority'] = each_ent.find_all('span',
                                              class_='textcor')[1].text.strip()

                self.qyxx_branch.append(info)

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self):

        url = ('http://%s/aiccips//PleInfo/PleInfoList' % self.host)
        response = url_requests.get(url=url,
                                    params=self.data,
                                    headers=self.headers,
                                    proxies=proxies)
        items = json.loads(response.text)['list']['list']  # type is list
        if items:
            for each_item in items:
                item = {}
                item['mortgage_reg_num'] = each_item.get('pleNo', '')
                item['date_reg'] = each_item.get('regiDate', '')
                if item['date_reg']:
                    # 将时间戳转换成日期
                    date = time.localtime(item['date_reg'] / 1000)
                    item['date_reg'] = time.strftime("%Y-%m-%d", date)
                item['authority'] = each_item.get('regOrgStr', '')
                item['amount'] = str(each_item.get('priClaSecAm', '')) + '万元'
                if '1' in each_item.get('type', ''):
                    item['status'] = '有效'
                else:
                    item['status'] = '无效'
                item['gongshiriqi'] = each_item.get('pefPerForm', '')
                if item['gongshiriqi']:
                    # 将时间戳转换成日期
                    date = time.localtime(item['gongshiriqi'] / 1000)
                    item['gongshiriqi'] = time.strftime("%Y-%m-%d", date)
                item['detail'] = each_item   # 后面通过这个信息里的字段获取详细信息

                self.qyxx_mortgage_basic.append(item)

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self):

        url = ('http://%s/aiccips//StoPleInfo/StoPleInfoList' % self.host)
        response = url_requests.get(url=url,
                                    params=self.data,
                                    headers=self.headers,
                                    proxies=proxies)
        items = json.loads(response.text)['list']['list']  # type is list
        if items:
            for each_item in items:
                item = {}
                item['reg_code'] = each_item.get('stoRegNo', '').strip()
                item['pleder'] = each_item.get('inv', '')
                item['id_card'] = each_item.get('invID', '')
                item['plede_amount'] = str(each_item.get('impAm', '')) + '万元'
                item['brower'] = each_item.get('impOrg', '')
                item['brower_id_card'] = each_item.get('impOrgID', '')
                item['reg_date'] = each_item.get('registDate', '')
                if item['reg_date']:
                    # 将时间戳转换成日期
                    date = time.localtime(item['reg_date'] / 1000)
                    item['reg_date'] = time.strftime("%Y-%m-%d", date)
                if '1' in each_item.get('type', ''):
                    item['status'] = '有效'
                else:
                    item['status'] = '无效'
                item['changes'] = '详情'

                self.qyxx_pledge.append(item)

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self):

        url = ('http://%s/aiccips//xzPunishmentList' % self.host)

        response = url_requests.get(url=url,
                                    params=self.data,
                                    headers=self.headers,
                                    proxies=proxies)
        items = json.loads(response.text)['list']['list']  # type is list
        if items:
            for each_item in items:
                item = {}
                item['pun_number'] = each_item.get('penDocNo', '')
                item['reason'] = each_item.get('illegalActType', '')
                item['fines'] = each_item.get('penalizeKind', '')
                item['authority'] = each_item.get('penAuthory', '')
                item['pun_date'] = each_item.get('penDecisionTime', '')
                if item['pun_date']:
                    # 将时间戳转换成日期
                    date = time.localtime(item['pun_date'] / 1000)
                    item['pun_date'] = time.strftime("%Y-%m-%d", date)

                self.qyxx_adm_punishment.append(item)

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self):

        key_list = ['xuhao', 'reason', 'date_occurred','authority_in',
                    'reason_out', 'date_out', 'authority_out']

        url = ('http://%s/aiccips/GSpublicity/GSpublicityList'
               '.html?service=cipUnuDirInfo') % self.host

        response = url_requests.post(url=url,
                                     data=self.data,
                                     headers=self.headers,
                                     proxies=proxies)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('tr', class_='tablebodytext')

        for item in items:
            info = {}
            values = item.find_all('td')
            if len(values) < 3:
                return []
            for i, key in enumerate(key_list):
                info[key] = values[i].text.strip()

            if info['authority_out'] == '' and info['authority_in']:
                info['authority'] = info.pop('authority_in')
                info.pop('authority_out')
            else:
                info['authority'] = info.pop('authority_out')
                info.pop('authority_in')

            self.qyxx_abnormal.append(info)

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self):

        key_list = ['xuhao', 'type', 'reason_in', 'date_in', 'authority_in'
                    'reason_out', 'date_out', 'authority_out']

        url = ('http://%s/aiccips/GSpublicity/GSpublicityList'
               '.html?service=cipBlackInfo') % self.host

        response = url_requests.post(url=url,
                                     data=self.data,
                                     headers=self.headers,
                                     proxies=proxies)
        soup = BeautifulSoup(response.text, 'lxml')
        items = soup.find_all('tr', class_='tablebodytext')

        for item in items:
            info = {}
            values = item.find_all('td')
            if len(values) < 3:
                return []
            print '广东省黑名单企业，请检查黑名单数据获取是否准确。'.encode('utf-8')
            for i, key in enumerate(key_list):
                info[key] = values[i].text.strip()
            if info['authority_out'] == '' and info['authority_in']:
                info['authority'] = info.pop('authority_in')
                info.pop('authority_out')
            else:
                info['authority'] = info.pop('authority_out')
                info.pop('authority_in')

            self.qyxx_abnormal.append(info)

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self):

        url = ('http://%s/aiccips//cipSpotCheInfo/cipSpotCheInfoList' %
                                                                    self.host)
        response = url_requests.get(url=url,
                                    params=self.data,
                                    headers=self.headers,
                                    proxies=proxies)
        items = json.loads(response.text)['list']['list']  # type is list
        if items:
            for each_item in items:
                item = {}
                item['authority'] = each_item.get('aicName', '')
                item['spot_type'] = each_item.get('typeStr', '')
                item['spot_date'] = each_item.get('insDate', '')
                if item['spot_date']:
                    # 将时间戳转换成日期
                    date = time.localtime(item['spot_date'] / 1000)
                    item['spot_date'] = time.strftime("%Y-%m-%d", date)
                item['spot_result'] = (each_item.get('inspectDetail', '')
                                .replace('1','正常')
                                .replace('2','未按规定公示年报')
                                .replace('3','未按规定公示其他应当公示的信息')
                                .replace('4','公示信息隐瞒真实情况、弄虚作假')
                                .replace('5','通过登记的住所（经营场所）无法联系')
                                .replace('6','不予配合情节严重')
                                .replace('7','该主体已注销')
                                .replace('8','该主体未建财务账')
                                .replace('9','其他'))

                self.qyxx_spot_check.append(item)

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self):

        url = ('http://%s/aiccips//judiciaryAssist/judiciaryAssistList' %
                                                                    self.host)
        response = url_requests.get(url=url,
                                    params=self.data,
                                    headers=self.headers,
                                    proxies=proxies)
        items = json.loads(response.text)['list']['list']  # type is list
        if items:
            for each_item in items:
                item = {}
                item['person'] = each_item.get('inv', '')
                item['stock'] = str(each_item.get('froAm', '')) + '万元人民币'
                item['court'] = each_item.get('froAuth', '')
                item['notice_number'] = each_item.get('froDocNo', '')
                item['status'] = each_item.get('frozState', '').strip()
                if item['status'] in ['1', '2', '3', '4']:
                    item['status'] = '冻结'
                elif item['status'] == '5':
                    item['status'] = '解除冻结'
                else:
                    item['status'] = '失效'

                self.qyxx_stock_freeze.append(item)

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self):
        """股权变更表发生了变化，字段不一样了。"""
        # url = ('http://%s/aiccips//GuQuan/GuQuanChangeList') % self.host
        # response = url_requests.get(url=url,
        #                             params=self.data,
        #                             headers=self.headers,
        #                             proxies=proxies)
        # items = json.loads(response.text)['list']['list']  # type is list
        # if items:
        #     for each_item in items:
        #         item = {}
        #         item['person'] = each_item.get('guDName', '')
        #         item['before'] = each_item.get('transBePr', '')
        #         item['after'] = each_item.get('transAfPr', '')
        #         item['change_date'] = each_item.get('altDate', '')
        #
        # # key_list = ['xuhao', 'person', 'stock', 'person_get', 'court',
        # #             'detail']

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, **kwargs):
        """只有mortgage_basic这个表有数据，才会执行下面三个附属表。"""
        soup = kwargs.get('mortSoup')
        table_tag= soup.find_all('div')
        for each in table_tag:
            if '动产抵押登记信息' in each.text:
                table = each.next_sibling.next_sibling
                keys = table.find_all('td', class_='tdTitleText')
                info = {}
                for each_key in keys:
                    key = each_key.text.strip()
                    value = each_key.next_sibling.next_sibling.text.strip()
                    info[key] = value

                info = common.c_mortgage_dict(info)
                self.mortgage_reg_num = info['mortgage_reg_num']
                self.qyxx_c_mortgage.append(info)
                break

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, **kwargs):
        soup = kwargs.get('mortSoup')
        table_tag = soup.find_all('div')
        for each in table_tag:
            if '被担保债权概况' in each.text:
                table = each.next_sibling.next_sibling
                keys = table.find_all('td', class_='tdTitleText')
                info = {}
                for each_key in keys:
                    key = each_key.text.strip()
                    value = each_key.next_sibling.next_sibling.text.strip()
                    info[key] = value
                info['mortgage_reg_num'] = self.mortgage_reg_num
                info = common.s_creditor_dict(info)
                self.qyxx_s_creditor.append(info)
                break

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, **kwargs):
        key_list = ['xuhao', 'mortgage_name', 'belongs',
                    'information', 'mortgage_range']
        soup = kwargs.get('mortSoup')
        table_tag = soup.find_all('div')
        for each in table_tag:
            if '抵押物概况' in each.text:
                table = each.next_sibling.next_sibling
                body = table.find_all('tr', class_='tablebodytext')
                info_list = []
                for each_row in body:
                    values = each_row.find_all('td')
                    info = {}
                    for i, key in enumerate(key_list):
                        info[key] = values[i].text.strip()
                    info['mortgage_reg_num'] = self.mortgage_reg_num
                    info_list.append(info)
                self.qyxx_mortgage.extend(info_list)
                break

def main(**kwargs):

    link = kwargs.get('id_tag')
    global proxies
    proxies = kwargs.get('proxies')

    # 广东，广州，深圳有不同的headers
    host = link.split('/')[2]
    headers = {
        'Host':host,
        'Referer':('http://gd.gsxt.gov.cn/aiccips/CheckEntContext/showCheck'
                  '.html'),
        'User-Agent':('Mozilla/5.0 (Windows NT 6.1; WOW64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/55.0.2883.87 Safari/537.36')
    }

    response = url_requests.get(url=link,
                                headers=headers,
                                proxies=proxies)

    soup = BeautifulSoup(response.text, 'lxml')

    req_data = {}
    try:
        req_data['entNo'] = soup.find('input', {'name': 'entNo'})['value']
        req_data['entType'] = soup.find('input', {'name': 'entType'})['value']
        req_data['regOrg'] = soup.find('input', {'name': 'regOrg'})['value']
    except Exception:
        raise IpRefused('系统无法显示，请返回操作！'.encode('utf-8'))

    all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute', 'member_execute',
        'branch_execute', 'mortgage_basic_execute', 'pledge_execute',
        'adm_punishment_execute', 'abnormal_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

    credit = Enterprise(host=host, headers=headers, data=req_data)

    for each in all_execute[:-3]:
        print "Executing: %s" % each
        getattr(credit, each)()
        # credit.member_execute()

    # 若存在动产抵押信息，则执行下文，若无，则不执行，不影响数据返回格式。
    if credit.qyxx_mortgage_basic:
        url = 'http://%s/aiccips/GSpublicity/GSpublicityList.html' % host
        for mortgage in credit.qyxx_mortgage_basic:
            detail = mortgage['detail']
            params = req_data
            params['service'] = 'pleInfoData'
            params['pleNo'] = detail.get('pleNo')
            params['type'] = detail.get('type')

            response = url_requests.get(url=url,
                                        params=params,
                                        headers=headers,
                                        proxies=proxies)
            soup = BeautifulSoup(response.text, 'lxml')
            for each in all_execute[-3:]:
                print "Executing: %s" % each
                getattr(credit, each)(mortSoup=soup)

    result_data = credit.returnData()

    return result_data

if __name__ == '__main__':

    # # 兴宁市中恒眼镜配件有限公司(变更有查看更多资料，经营异常，抽查)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_N36dYNuUTaB78O3n9De28Gg/Dgnzvw1Q'
    #         '+YrGtoZi2XdTAOYLpc4gxgb5a3wjX8k3-tF6QxU8NH+larVWkm1M5Vg==')

    # # 东莞市友谊国际劳务有限公司 (股东多页)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_Se30rZJVgWG459'
    #         '/tKQrYrOUZCdj7G5CrbDs6WUvrvBmfmyhBDv7NveR1uYRpZWc'
    #         '+-QuOaBlqqlUykdKokb5yijg==')

    # # 广州腾讯科技有限公司 (变更信息)
    # link = ('http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_nPNw57QPCnL961TNeXO4Gqc'
    #         '/FgBy7ESTwWPrP4zJe5g=-FBrJ/suNwXMupXtmIUvNKg==')

    # # 广东永航新材料实业股份有限公司 (动产抵押)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_kjBa3yRFyaNyn6Btv73yqSkaPF9MYVyWwnMkTfDAX3F'
    #         'TAOYLpc4gxgb5a3wjX8k3-Yo1vDaPPmlocGn8BN2rqNg==')

    # # 肇庆粤肇公路有限公司(股权出资)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_a0bFsn'
    #         '/9SZe007U1MYqw5Bl6EcMH9tucB1dS80gFxOqVnZGcb55Y7vPdAYLPm2hF'
    #         '-Qvcdhrd7jiCXpDdG6OWFEQ==')

    # # 汕头市伟业化妆品有限公司(行政处罚)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_g3g3qEu85CorgSMmL39vTqFSvzSuWDvvsSjAGkyqUB5'
    #         'TAOYLpc4gxgb5a3wjX8k3-djd0qvgI9W8keRTvFg3F0g==')

    # # 广东阳东农村商业银行股份有限公司(股东冻结)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_uEDfBZsY517f'
    #         '/parCAWfBT2p0J5O54edGBkVQ1gT9vZTAOYLpc4gxgb5a3wjX8k3'
    #         '-BtSeBr4lXkWEPs2t0/pAdQ==')

    # # 广州市海珠区琶洲旺强商行(经营异常)
    # link = ('http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_9D6cmG2K0KHgx25Me'
    #         'ScfnFuYngXwcHsV2PLbtz3fAhY=-FBrJ/suNwXMupXtmIUvNKg==')

    # # 广东肇庆动力金属股份有限公司(抽样调查)
    # link = ('http://gsxt.gdgs.gov.cn/aiccips/GSpublicity/GSpublicityList'
    #         '.html?service=entInfo_nXAHsCw4gWyFNyRBjOuRdpk1uTOSKdScmLfgFWmt'
    #         'DT2UTTm6KplcstVhvTbT4e2Y-Qvcdhrd7jiCXpDdG6OWFEQ==')

    # 广州市花都华美实业有限公司(股权变更)
    link = ('http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList'
            '.html?service=entInfo_28C7difAxzPuIxlNTjzUri2qxDpKNjkT'
            '+FOpraFOZa4=-kW1OV14JwB9Mxg2tkeoAzw==')

    # 广州市越秀区浍雅工艺美术品经营部
    link = ('http://gsxt.gzaic.gov.cn/aiccips/GSpublicity/GSpublicityList'
            '.html?service=entInfo_0OGd7yfVOEbNNAg+9MJn4ArCZYRFCYFBGO'
            '/MqqyzGZI=-MYLds2BkfQ6TcJNl3kL0ng==')
    proxies = {
        'http': 'http://120.76.138.208:2323',
        'https': 'http://120.76.138.208:2323'
    }
    main(id_tag=link)