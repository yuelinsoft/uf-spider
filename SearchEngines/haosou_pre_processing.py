#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

"""
    haosou_pre_processing
    ~~~~~~~~~

    好搜爬虫任务字典分发

    :copyright: (c) 2017 by cds@uf-club.
    :license: MIT, see LICENSE for more details.
"""

__versions__ = '5.0.1'

from SearchEngines.haosou_config import *
from SearchEngines.exception_handle import exception_raise


def original_task_mapping(data_dict):
    """已有的任务字典分发，映射成多个字典列表

    :param data_dict: 已有的任务字典
    :return: 内容字典列表
    """
    task_info_list = list()
    for task_key in data_dict.keys():
        task_value = data_dict[task_key]
        # 空值不查
        if task_value in ['', ' ', None, False]:
            # print('{}: null value'.format(task_key))
            continue
        # 非查询字段不查
        if task_key not in QUERY_KEY:
            print('{}({}) not in query list'.format(task_value, task_key))
            continue
        # 敏感词不查
        if task_value in BLACK_LIST_MAP:
            if task_value in BLACK_LIST_MAP[task_key]:
                print('{}({}) in black list'.format(task_value, task_key))
                continue
        pages = PAGE_DICT.get(task_key, None)
        if pages:
            for page in range(1, pages+1):
                task_info_list.append(dict(data={task_key: task_value},
                                           page=page))
        else:
            print('{}({}): null page'.format(task_value, task_key))
            continue
    return task_info_list


def compositive_task_mapping(data_dict):
    """已有的任务字典分发，映射成多个新组合的字典列表

    :param data_dict: 已有的任务字典
    :return: 新组合的字典列表
    """
    task_info_list = list()
    for new_key in COMPOSITE_KEY_DICT.keys():
        if new_key not in data_dict:
            composite_value_list = COMPOSITE_KEY_DICT[new_key]
            temp_value_list = []
            for composite_key in composite_value_list:
                if not isinstance(composite_key, list):
                    temp_value = data_dict.get(composite_key, None)
                    if temp_value:
                        temp_value_list.append(temp_value)
                else:
                    temp_value_list.append(composite_key[0])
            if '' in composite_value_list or None in composite_value_list:
                continue
            else:
                composite_value = ' '.join(temp_value_list)
                if composite_value == '':
                    continue
                pages = PAGE_DICT.get(new_key, None)
                if pages:
                    for page in range(1, pages+1):
                        task_info_list.append(
                            dict(data={new_key: composite_value},
                                 page=page))
                else:
                    print('{}({}): null page'.format(composite_value, new_key))
    return task_info_list


def task_assignment(data_dict):
    """任务字典分发,映射成多个字典列表

    :param data_dict: 任务字典
    :return: 内容字典列表
    """
    if len(data_dict.keys()) == 0:
        exception_raise(KeyError, msg='No Info Inside')
    # 字典中已有的 k-v 映射
    task_info_list = original_task_mapping(data_dict)
    # 新组合的 k-v 映射
    task_info_list.extend(compositive_task_mapping(data_dict))
    if len(task_info_list) == 0:
        exception_raise(KeyError, msg='No Info Inside')
    return task_info_list


def main(**kwargs):
    """主函数

    :param kwargs: 传入参数，proxies，data, page...
    :return: 内容字典
    """
    try:
        data = kwargs.get('data')
        task_info_list = task_assignment(data)
        return 'SearchEngines.haosou_crawler', task_info_list
    except Exception as e:
        if hasattr(e, 'uf_errno') and e.uf_errno:
            raise
        exception_raise(e, code=101)


def start(**kwargs):
    """分布式调用函数

    :param kwargs: 传入参数，proxies，data, page...
    :return: 内容字典
    """
    return main(**kwargs)


if __name__ == '__main__':
    task = dict(data={'name': '冯君贤',
                      'id_num': '441827198609147000',
                      'phone1': '13363446295',
                      'phone2': '13363446294',
                      'phone3': '13363446293',
                      'company': '上海基础工程集团有限公司',
                      'company_phone1': '0532-58731555',
                      'company_phone2': '',
                      'company_phone3': '',
                      'spouse_name': '梁嘉雯',
                      'spouse_id_card': '441802198407260000',
                      'spouse_phone1': '13924413871',
                      'spouse_phone2': '13924413872',
                      'contact_phone1': '13631054187',
                      'contact_phone2': '15972171851',
                      'contact_phone3': '15992088600',
                      'contact_phone4': '13826265800',
                      'contact_phone5': '13826265801',
                      'contact_phone6': '13826265802',
                      'contact_phone7': '13826265803',
                      'contact_phone8': '13826265804',
                      }
                )
    print(start(**task))