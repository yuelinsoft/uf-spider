#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

"""
    operator_controller
    ~~~~~~~~~

    运营商函数集成

    :copyright: (c) 2017 by cds@uf-club.
    :license: MIT, see LICENSE for more details.
"""

__versions__ = '0.0.0'

import importlib
from OperatorCrawler.public.get_phone_attr import get_phone_attr, return_result


def start(**kwargs):
    """分布式调用函数

    :param kwargs: 传入参数，proxies, province, data...
    :return: 内容字典
    """
    # TODO: 代理 IP 入口待接入
    proxies = kwargs.get('proxies')
    operator = kwargs.get('operator')
    data = kwargs.get('data')

    phone_num = data.get('phone_num')
    password = data.get('password')
    sms_code = data.get('sms_code')
    try:
        # 判断省份是否有效
        if operator=='china_mobile':
            # e.g. province = 'china_mobile-d1_guangdong'
            exec_module = (importlib.import_module('OperatorCrawler.{op}.{op}.{prov}_crawler'
                                                   .format(op=operator)))
            # TODO: send_code, login_for_crawler 函数名待统一
            if phone_num and password and len(sms_code) == 0:
                data.pop('sms_code')
                return exec_module.send_code(**data)
            elif phone_num and password and len(sms_code) > 0:
                return exec_module.login_for_crawler(phone_num, password, sms_code)
        elif operator=='china_unicom':
            # 根据号码进行分发[目前只支持中国联通]
            phone_attr = get_phone_attr(phone_num)
            if phone_attr['code'] == 2000:
                phone_attr = phone_attr['data']
                if phone_attr['company'] == 1:  # 联通
                    phone_attr['password'] = password
                    exec_module = (importlib.import_module('OperatorCrawler.{op}.{op}'.format(op=operator)))
                    return exec_module.handle_ChinaUnicom(phone_attr)
                else:
                    return return_result(
                        code=4400,
                        data={},
                        desc=u'目前仅支持联通查询'
                    )
            else:
                return return_result(
                    code=4800,
                    data={},
                    desc=u'查询手机属性外部接口失败'
                )
    except Exception as e:
        print e
        # TODO: 定义公用的异常类


if __name__ == '__main__':
    task = dict(proxies=None, operator='china_unicom',
                data=dict(phone_num='', password=''))
    print start(**task)