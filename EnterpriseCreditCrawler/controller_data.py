# -*- coding: utf-8 -*-
"""
    __author__ = 'LiJianBin'

    [controller_data]用途：
    企业信用爬虫系统中，获取【详细页面】数据的总控脚本程序。

"""
from __future__ import unicode_literals
import importlib
from EnterpriseCreditCrawler.common import conf
from EnterpriseCreditCrawler.common.uf_exception import (UfException,
                                                         ServiceError,
                                                         ParameterError,
                                                         IpRefused)

def start(**kwargs):
    """分布式查询启动入口, kwargs必须包含键data，data包含enterprise_credit_status，
    province， link（query的结果）。

    """

    data_tag = kwargs.get('data')
    proxies = kwargs.get('proxies')
    params = data_tag.get('enterprise_credit_status')  # dict
    company_city = params.get('company_city')
    company = params.get('company')

    try:
        id_tag = data_tag.get('detail')
        province = data_tag.get('province')
        # 再次判断省份是否提供查询服务
        if 'szcredit' in id_tag:
            raise ParameterError("该企业属于深圳市，请更正后重查。".encode('utf-8'))
        elif province in conf.provDict.keys():
            prov_data_module = importlib.import_module(
                "EnterpriseCreditCrawler.crawler." + conf.provDict[province] +
                "_data")
        else:
            prov_data_module = importlib.import_module(
                "EnterpriseCreditCrawler.crawler.main_entrance_data")

        detail_dict = prov_data_module.main(id_tag=id_tag, proxies=proxies)

        # 对查询结果做判断
        if detail_dict:
            if '深圳' in province:
                has_company_name =  detail_dict['qyxx_sz_basicinfo'][0].get(
                    'company_name')
            else:
                has_company_name = detail_dict['qyxx_basicinfo'][0].get(
                    'company_name')
            if has_company_name:
                params.update({'province': province})

                return params, detail_dict
            else:
                raise IpRefused('query successful, but data failed.')

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
            print '网络异常导致数据解析失败：'
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
    "data": {"prov":"e3_hunan",
    "link":'/businessPublicity.jspx?id=94EC2DC6E1F53A7E1D12A0844F0A8380'}
    }
    或如下：
    {
    "msg_no":"1",
    "data": {"prov":"e3_hunan", "link":([u'5009051201409010680726',
    u'500905305254307',u'\u6df1\u5733\u524d\u6d77\u878d\u91d1\u6240\u57fa
    \u91d1\u7ba1\u7406\u6709\u9650\u516c\u53f8\u91cd\u5e86\u5206\u516c\u53f8
    ',u'2130'])}，
    }

   =========================================================
    【输出端】 detail_dict 数据类似如下：
    [
        {
        'province': '广州'
        }，

        {
        'table_0':[
                    {'key_0':'key_0's value in line_0',
                    'key_1':'key_1's value in line_0'},

                    {'key_0':'key_0's value in line_1',
                    'key_1':'key_1's value in line_1'}
                    ],
        'table_1':[
                    {'key_0':'key_0's value in line_0',
                    'key_1':'key_1's value in line_0'},

                    {'key_0':'key_0's value in line_1',
                    'key_1':'key_1's value in line_1'}
                    ]
        }
    ]
    """

    data = {u'province': u'广州', u'link':
        '/businessPublicity.jspx?id=F205E2C91F5E1268263DACC0B9897BEF'}

    symbol, detail_dict = start(msg_no="1",data=data)

    print detail_dict