# -*- coding: utf-8 -*-
from __future__ import unicode_literals
"""
使用百度失信的接口进行爬取
"""

import re
import json

import requests


class BaiduShixinSpider(object):
    def __init__(self):
        self.url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) '
                          'AppleWebKit/537.36 (KHTML, like Gecko)'
                          ' Chrome/56.0.2924.87 Safari/537.36',
            'Host': 'sp0.baidu.com',
        }

    def query_data(self, relation_ship, name, card_num=None, proxies=None):
        # 过滤非法参数
        if is_params_illegal(name):
            return dict(
                status=2100,
                name=name,
                id_num=card_num,
                relationship=relation_ship,
                info=tuple()
            )

        params = {
            'resource_id': '6899',
            'query': '失信被执行人名单',
            'iname': name,
            'cardNum': card_num,
            'ie': 'utf-8',
            'oe': 'utf-8',
            'format': 'json',
            'cb': 'jQuery110208320092000673853_1488943361816',
        }
        resp = requests.get(self.url, headers=self.headers, params=params)
        if not resp or resp.status_code != 200:
            raise Exception('requests failed')
        content = resp.content
        pattern = re.compile('\((.*)\)', re.S)
        match_obj = re.search(pattern, content)
        if not match_obj:
            print 'failed'
            item_list = []
        else:
            result = match_obj.group(1)
            info = json.loads(result)
            data_list = info.get('data')
            if not data_list or len(data_list) <= 0:
                print 'have no data'
                item_list = []
            else:
                item_list = data_list[0].get('result')
                item_list = self.construct_data(item_list)

        status = 2000 if len(item_list) else 2100
        return dict(
            status=status,
            name=name,
            id_num=card_num,
            relationship=relation_ship,
            info=tuple(item_list)
        )

    @staticmethod
    def construct_data(item_list):
        """将源数据转化为数据库中对应的数据"""
        if not item_list or len(item_list) <= 0:
            return

        new_item_list = []
        for item in item_list:
            new_item = dict()
            new_item['sys_id'] = None
            loc = item.get('loc', None)
            if loc:
                sys_id = re.search('id=(\d*)', loc)
                if sys_id:
                    new_item['sys_id'] = sys_id.group(1)
            new_item['name'] = item.get('iname', None)
            new_item['age'] = item.get('age', None)
            new_item['sex'] = item.get('sexy', None)
            new_item['card_num'] = item.get('cardNum', None)
            new_item['business_entity'] = item.get('businessEntity', None)
            new_item['area_name'] = item.get('areaName', None)
            new_item['case_code'] = item.get('caseCode', None)
            new_item['reg_date'] = item.get('regDate', None)
            new_item['publish_date'] = item.get('publishDate', None)
            new_item['gist_id'] = item.get('gistId', None)
            new_item['court_name'] = item.get('courtName', None)
            new_item['gist_unit'] = item.get('gistUnit', None)
            new_item['duty'] = item.get('duty', None)
            new_item['performance'] = item.get('performance', None)
            new_item['disrupt_type_name'] = item.get('disruptTypeName', None)
            new_item['party_type_name'] = item.get('partyTypeName', None)
            # 通过age判断是否为个人，个人设置flag为0，公司设置为1
            if not new_item['age'] or new_item['age'] == '0':
                new_item['flag'] = 1
            else:
                new_item['flag'] = 0
            new_item_list.append(new_item)
        return new_item_list


def is_params_illegal(check_item):
    """对于非正常数据不进行失信查询，相应数据由产品提供"""
    illegal_params_list = ['居家', '老婆']
    if not check_item or check_item in illegal_params_list:
        return True
    return False


def start(**kwargs):
    """ 分布式接入接口
    :return: 参考__intro__ """
    # proxies = kwargs.get('proxies')

    data = kwargs.get('data')
    name = data.get('name')               # 借款人姓名
    card_num = data.get('id_num')          # 借款人身份证号
    company = data.get('company')         # 借款人就职公司

    spouse_name = data.get('spouse_name')         # 配偶姓名
    spouse_card_num = data.get('spouse_id_card')   # 配偶身份证号
    spouse_company = data.get('spouse_company')   # 配偶就职公司

    spider = BaiduShixinSpider()
    result = []
    if name:
        borrower = spider.query_data('个人', name, card_num)
        if borrower:
            result.append(borrower)
    if company:
        borrower_company = spider.query_data('借款人就职公司', company)
        if borrower_company:
            result.append(borrower_company)
    if spouse_name and spouse_card_num:
        spouse = spider.query_data('配偶', spouse_name, spouse_card_num)
        if spouse:
            result.append(spouse)
    if spouse_company:
        spouse_company = spider.query_data('配偶就职公司', spouse_company)
        if spouse_company:
            result.append(spouse_company)
    return result


def main():
    info = dict(
        proxies=None,
        data={
            'name': '杨梦乱',
            'id_num': '4264354333223',
            'company': '石家庄市建业房地产开发有限公司',
            'spouse_name': '黄色阳',
            'spouse_id_card': '370921196712343620',
            'spouse_company': '居家',
        }
    )
    results = start(**info)
    print results


if __name__ == '__main__':
    main()
