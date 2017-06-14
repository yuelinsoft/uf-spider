# -*- coding: utf-8 -*-
"""
    __author__ = 'KEXH'

    [controller_query]用途：
    企业信用爬虫系统中，获取【列表页面】数据的总控脚本程序。

"""


from __future__ import unicode_literals
import importlib
import Levenshtein
from EnterpriseCreditCrawler.common import conf, common
from EnterpriseCreditCrawler.common.uf_exception import (ParameterError,
                                                         SuccessNoData,
                                                         UfException)

def start(**kwargs):
    """分布式查询入口，kwargs必须包含键data。data包含company和company_city"""

    search_tag = kwargs.get('data')
    proxies = kwargs.get('proxies')

    company_city = search_tag.get('company_city')
    company = search_tag.get('company')

    try:
        if not company_city or not company:
            raise ParameterError("The parameters not has key company or "
                                 "company_city")

        # 判断company_city是哪个省
        province = common.judge_province(company_city, conf.provDict)

        # 判断省份是否有效
        if province:
            if province == '广州':
                prov_query_module = importlib.import_module(
                "EnterpriseCreditCrawler.crawler." + conf.provDict['广东'] +
                "_query")
            else:
                prov_query_module = importlib.import_module(
                "EnterpriseCreditCrawler.crawler." + conf.provDict[province] +
                "_query")
        else:
            province = company_city
            prov_query_module = importlib.import_module(
                "EnterpriseCreditCrawler.crawler.main_entrance_query")

        # 查询入口(失败重跑2次)
        retry = 0
        items = [{}]    # 声明一个空的字典列表
        while retry < 3:
            try:
                items = prov_query_module.main(name=company, proxies=proxies)
                break
            except Exception as e:
                retry += 1
        if retry == 3:
            raise
        # 判断是否查询到结果
        match_list = []
        similar_list = []
        if items:
            for item in items:
                search_company = item['company']
                distance = Levenshtein.ratio(company.strip(),
                                             search_company.strip())
                enterprise_credit_status = {
                    'similarity': '%.2f' % (round(distance, 4) * 100),
                    'company_city': company_city,
                    'company': search_company,
                    'enterprise_credit_status': 2000,
                }
                data = {
                    'enterprise_credit_status': enterprise_credit_status,
                    'province': province,
                    'detail': item['detail']
                }
                if company.strip() == search_company.strip():   # 只返回名称一致的数据
                    match_list.append(data)
                else:
                    similar_list.append(data)
            next = "EnterpriseCreditCrawler.controller_data"

            if match_list:
                # 存在精确匹配
                return next, match_list
            elif similar_list:
                # 没有精确匹配，有模糊匹配
                similar_list = sorted(similar_list,
                                      key=lambda data: data[
                                          'enterprise_credit_status'][
                                          'similarity'],
                                      reverse=True)
                return next, similar_list[:5]
            else:
                raise SuccessNoData('Success, not result.')
                # 有结果，但不满足匹配条件
        else:
            raise SuccessNoData('Success, not result.')
            # return None, enterprise_credit_status     # 没有结果

    except Exception as err:
        if isinstance(err, UfException):
            err.uf_msg = err.message  # 将异常信息保存到 uf_msg 里面
            err.enterprise_credit_status = {
                'company_city': company_city,
                'company': company,
                'enterprise_credit_status': err.status_code
            }
            raise
        else:
            # print '出现网络异常：'
            err.uf_errno = 100
            err.uf_msg = err.message
            err.enterprise_credit_status = {
                'company_city': company_city,
                'company': company,
                'enterprise_credit_status': 4000
            }

            raise


if __name__ == '__main__':
    """
    【输入端】 kwargs 数据类似如下：
    {
    "msg_no":"1",
    "data": {
        "name":u"朱月英",
        "id_num":"43250219680****3835",
        "phone1":"18503008520",
        "phone2":"18503008521",
        "phone3":"18503008522",
        "company":u"湖南国腾讯达信息科技有限公司",
        "company_phone1":"18503008523",
        "company_phone2":"18503008524",
        "company_phone3":"18503008525",
        "company_address":u"福田",
        "company_city":u"福田",
        "spouse_name":u"张三妻",
        "spouse_id_card":"43250219680****3834",
        "spouse_phone1":"18503008526",
        "spouse_phone2":"18503008527",
        "address":u"湖南",
        "contact_name1":u"张三友1",
        "contact_relationship1":u"朋友",
        "contact_phone1":"18503008528",
        "contact_name7":u"张三友7",
        "contact_relationship7":u"朋友",
        "contact_phone7":"18503008514",
        "contact_name8":u"张三友8",
        "contact_relationship8":u"朋友",
        "contact_phone8":"18503008515",
    }
}
    =========================================================
    【输出端】 result_list 数据类似如下：
    [
    {"province":"湖南", "link":'/businessPublicity.jspx?id
    =94EC2DC6E1F53A7E1D12A0844F0A8380'},

    {"province":"湖南",
    "link":'/businessPublicity.jspx?id=B95CA6533683CD5F43F17AA6EB289D85'}
    ]
    或如下：
    [
        {"province":"湖南", "link":[u'5009051201409010680726',
        u'500905305254307',
        u'\u6df1\u5733\u524d\u6d77\u878d\u91d1\u6240\u57fa\u91d1\u7ba1\u7406
        \u6709\u9650\u516c\u53f8\u91cd\u5e86\u5206\u516c\u53f8',u'2130']}，

        {"province":"湖南", "link":[u'5000001201405210547623',
        u'500103000851800',
        u'\u91cd\u5e86\u60e0\u6c11\u91d1\u878d\u670d\u52a1\u6709\u9650\u8d23
        \u4efb\u516c\u53f8', u'1140']}，

        {"province":"湖南", "link":[u'500225010100001054',
        u'500225300003593',
        u'\u91cd\u5e86\u5e02\u5927\u8db3\u804c\u4e1a\u6280\u672f\u6559\u80b2
        \u540e\u52e4\u670d\u52a1\u4e2d\u5fc3', u'4320']}
    ]
    """

    data={
            "name": u"朱月英",
            "id_num": "43250219680****3835",
            "phone1": "18503008520",
            "phone2": "18503008521",
            "phone3": "18503008522",
            "company": u'腾讯',
            "company_phone1": "18503008523",
            "company_phone2": "18503008524",
            "company_phone3": "18503008525",
            "company_address": u"广东",
            "company_city": u"广东",
            "spouse_name": u"张三妻",
            "spouse_id_card": "43250219680****3834",
            "spouse_phone1": "18503008526",
            "spouse_phone2": "18503008527",
            "address": u"湖南",
            "contact_name1": u"张三友1",
            "contact_relationship1": u"朋友",
            "contact_phone1": "18503008528",
            "contact_name7": u"张三友7",
            "contact_relationship7": u"朋友",
            "contact_phone7": "18503008514",
            "contact_name8": u"张三友8",
            "contact_relationship8": u"朋友",
            "contact_phone8": "18503008515",
        }
    next, result_list = start(msg_no="1",data=data)
    print result_list

