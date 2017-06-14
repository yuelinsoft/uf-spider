#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

"""
    haosou_crawler
    ~~~~~~~~~

    好搜爬虫，输入关键字，返回筛选过的搜索信息

    :copyright: (c) 2017 by cds@uf-club.
    :license: MIT, see LICENSE for more details.
"""

__versions__ = '5.0.1'

import copy
import re
import requests

from requests.exceptions import HTTPError
from exception_handle import exception_raise
from haosou_config import *


def generate_urls(url_template, query_term_list):
    """按照相应模板的 URL 生成器

    :param url_template: URL 模板列表，需要适配 format() 函数('{}')
    :param query_term_list: [{'key': 'value'}, {'key': 'value'}...]
    :return: 含有参数的 URL 生成器
    """
    for query_term_dict in query_term_list:
        yield url_template.format(**query_term_dict)


def get_response(urls, method='GET', data=None, proxies=None, headers=None):
    """执行页面请求

    :param urls: URL 列表，同 Requests 参数要求
    :param method: 默认为 ‘GET’ 方式请求，同 Requests 参数要求
    :param data: 为 ‘POST’ 时所携带的参数，同 Requests 参数要求
    :param proxies: 代理，同 Requests 参数要求
    :param headers: 请求头，同 Requests 参数要求
    :return: Class Response from Requests lib
    """
    request_list = []
    for i, url in enumerate(urls):
        try:
            resp = requests.request(method=method, url=url, proxies=proxies,
                                    data=data[i] if data else None, timeout=10,
                                    allow_redirects=False, headers=headers,
                                    verify=False)
            request_list.append(resp)
        except Exception as e:
            exception_raise(e, msg=url)
    return request_list


def run_request(url_template, query_term_list, method='GET', data=None,
                proxies=None, headers=None):
    """生成 URL 模板并请求网页

    :param url_template: URL 模板列表，需要适配 format() 函数('{}')
    :param method: 默认为 ‘GET’ 方式请求，同 Requests 参数要求
    :param data: 为 ‘POST’ 时所携带的参数，同 Requests 参数要求
    :param proxies: 代理，同 Requests 参数要求
    :param headers: 请求头，同 Requests 参数要求
    :return: get_response()
    """
    urls = generate_urls(url_template, query_term_list)
    return get_response(urls, method=method, data=data, proxies=proxies,
                        headers=headers)


def url_request(url_template, query_term_list, method='GET', data=None,
                proxies=None, headers=None):
    """发起网页请求

    :param url_template: URL 模板列表，需要适配 format() 函数('{}')
    :param query_term_list: URL 参数列表
    :param method: 默认为 ‘GET’ 方式请求，同 Requests 参数要求
    :param data: 为 ‘POST’ 时所携带的参数，同 Requests 参数要求
    :param proxies: 代理，同 Requests 参数要求
    :param headers: 请求头，同 Requests 参数要求
    :return: Requests Object list
    """
    result = run_request(url_template, query_term_list, method=method,
                         data=data, proxies=proxies, headers=headers)
    return result


def keyword_query(keyword_dict, page=1, proxies=None, headers=None):
    """查询关键词

    :param keyword_dict: 查询参数字典
    :param page: 页数
    :param proxies: 代理，同 Requests 参数要求
    :param headers: 请求头，同 Requests 参数要求
    :return: Requests Object dict
    """
    keyword_query_dict = copy.deepcopy(keyword_dict)
    query_type = keyword_query_dict['query_type']
    if query_type in CHECK_TIME_MAP:
        query_term_list = [dict(query_term=keyword_query_dict['query_term'],
                                page=page, time=CHECK_TIME_MAP[query_type])]
        query_url = HAOSO_URL_WITH_TIME
    else:
        return False
    content_list = url_request(query_url, query_term_list,
                               proxies=proxies, headers=headers)
    try:
        if content_list[0].status_code == requests.codes.ok:
            if not re.search(REGEX_PAGE_EXCEPTION,
                             content_list[0].content.decode('utf-8',
                                                            errors='ignore')):
                keyword_query_dict.update(content=content_list[0])
                return keyword_query_dict
            else:
                print('[PAGE EXCEPTION]:{}, {}, {}'.format(keyword_dict, page,
                                                           proxies))
                exception_raise(HTTPError('keyword_query(): PAGE EXCEPTION'),
                                code=102)
        else:
            content_list[0].raise_for_status()
    except Exception as e:
        exception_raise(e, msg=keyword_dict)


def info_query(info_dict, page=1, proxies=None):
    """发起关键字查询请求

    :param info_dict: 查询参数字典
    :param page: 页数
    :param proxies: 代理，同 Requests 参数要求
    :return: Requests Object dict
    """
    if info_dict is not False:
        if info_dict == dict():
            return dict()
    else:
        return False
    # if proxy_ip and PROXY_HOST:
    #     proxy = dict()
    #     for host in PROXY_HOST:
    #         proxy.update({host: proxy_ip})
    # else:
    #     proxy = None
    query_page_dict = keyword_query(info_dict, page, proxies, SO_HEADERS)
    return query_page_dict if query_page_dict else False


def re_message(regex_str, raw_content, mode=False):
    """In this function, it will use RegEx for string.

    :param regex_str: RegEx string
    :param raw_content: raw content
    :param mode: only return a value with first index of list
    :return: a list of matching content or None(no match info)

    Example:

    # >>>re_message('a(.*?)c', 'abc')
    # ['b']
    # >>>re_message('a(.*?)c', 'abd')
    # False

    """
    try:
        content_list = re.findall(regex_str, unicode(raw_content))
        if len(content_list) == 0 or content_list[0] == '':
            return None
        else:
            return content_list if not mode else content_list[0]
    except:
        return None


def get_result_info(content):
    """解析页面内每条条目内容

    :param content: html 内容
    :return: 匹配后的信息
    """
    # 如果手机存在所有人信息，则保留
    holder = re.search(REGEX_IMG_SCR, content)
    if holder:
        return ('电话号码归属地查询', FORMAT_IMG_SCR.format(holder.group(1)), None,
                '360手机应用', None)
    title = re.search(REGEX_TITLE, content)
    if not title:
        title = summary = cached_url = source = post_time = None
        return title, summary, cached_url, source, post_time
    else:
        title = title.group(1)
        try:
            summary_type = re.search(REGEX_SUMMARY_TYPE, title).group(0)
            summary = '&'.join(re_message(SUMMARY_SWITCH_DICT[summary_type],
                                          content))
        except:
            summary = re_message(REGEX_SUMMARY, content, mode=True)
    if not summary:
        summary = re_message(REGEX_SUMMARY_OTHER, content, mode=True)
    official = re.search(REGEX_OFFICIAL, content)
    if official:
        if summary:
            summary = FORMAT_OFFICIAL_TITLE.format(summary)
        else:
            summary = FORMAT_OFFICIAL_TITLE.format('')
    cached_url = re_message(REGEX_CACHED_URL, content, mode=True)
    if not cached_url:
        cached_url = re_message(REGEX_HOME_URL, content, mode=True)

    source = re_message(REGEX_SOURCE, content, mode=True)
    time_meta_data = re_message(REGEX_POST_TIME, content, mode=True)
    if time_meta_data:
        post_time = (FORMAT_POST_TIME.format(time_meta_data[0],
                                             time_meta_data[1],
                                             time_meta_data[2]))
    else:
        post_time = None
    return title, summary, cached_url, source, post_time


def page_parse(page_dict, page, top_size='max'):
    """解析页面内容

    :param page_dict: 返回页面信息字典
    :param page: 页数
    :param top_size: 解析页面的前 N 个条目, 默认为前 10 条，等于“max”时，整页解析
    :return: 匹配后的字典或 False
    """
    page_result_dict = copy.deepcopy(page_dict)
    try:
        content = page_result_dict['content'].content.decode('utf-8',
                                                             errors='ignore')
    except Exception as e:
        exception_raise(e, msg=page_result_dict)
    items_list = re_message(REGEX_PAGE_ITEM, content)
    page_map_list = list()
    if not items_list:
        # TODO: 无法解析和号码类分类
        return list()
    else:
        # 号码类查询去掉页面第一个条目（号码查询应用），公司号码的号码应用如有所有人则保留
        if page_result_dict['query_type'] in ID_CARD_MAP_KEY + PHONE_MAP_KEY:
            if page_result_dict['query_type'] in COMPANY_PHONE_KEY:
                if not re.search(REGEX_IMG_SCR, items_list[0]) or page != 1:
                    items_list = items_list[1:]
            else:
                items_list = items_list[1:]
        # 可设置只解析一个页面的前 N 个条目
        if top_size == 'max':
            top_size = len(items_list)
        for i, item in enumerate(items_list[: top_size]):
            title, summary, cached_url, source, post_time = \
                get_result_info(item)
            if title:
                page_map_list.append(dict(title=title, summary=summary,
                                          source=source, sequence_record=i,
                                          cached_url=cached_url,
                                          post_time=post_time,
                                          query_platform='好搜',
                                          cache_status=True,
                                          query_term=
                                          page_result_dict['query_term'],
                                          query_type=
                                          page_result_dict['query_type']))
    return page_map_list


def info_parse(page_dict, page):
    """发起页面解析

    :param page_dict: 返回信息字典
    :param page: 页数
    :return: 匹配后的字典列表
    """
    if page_dict is not False:
        if page_dict == dict():
            return list()
    else:
        return False
    try:
        page_parse_list = page_parse(page_dict, page)
        return page_parse_list
    except Exception as e:
        exception_raise(e, msg=page_dict)


def info_identical(items_list):
    """信息精确匹配

    :param items_list: 单个条目列表
    :return: 过滤后的字典列表
    """
    if items_list is not False:
        if items_list == list():
            return list()
    else:
        return False
    page_items_list = items_list[:]
    identical_list = list()
    query_term = page_items_list[0].get('query_term', 'None')
    for page_item in page_items_list:
        summary = page_item.get('summary',
                                'Null') if page_item.get('summary',
                                                         'Null') else ''
        # TODO: 避免: unbalanced parenthesis
        # if re.search(query_term, summary):
        # 如果存在公司号码所有人不需要经过精确匹配 <img src...>
        if query_term in summary or 'img src="data' in summary:
            identical_list.append(page_item)
    # 只查一页的类型则最多返回 5 条
    if len(identical_list) != 0:
        if PAGE_DICT[identical_list[0]['query_type']] == 1:
            return identical_list[:5]
    return identical_list


def repetition_filter(items_list):
    """重复信息过滤

    :param items_list: 单个条目列表
    :return: 重复信息索引
    """
    index_list = range(0, len(items_list))
    title_list = [item['title'] for item in items_list]
    summary_list = [item['summary'] for item in items_list]
    unique_title_index_list = dict(zip(title_list, index_list)).values()
    unique_summary_index_list = dict(zip(summary_list, index_list)).values()
    return list(set(unique_title_index_list) | set(unique_summary_index_list))


def source_filter(items_list):
    """网页来源过滤

    :param items_list: 单个条目列表
    :return: 匹配索引
    """
    summary_list = [item['summary'] for item in items_list]
    source_list = [item['source'] for item in items_list]
    official_index_list = [i for i, summary in enumerate(summary_list) if
                           summary and re.search('【官网】', summary)]
    source_index_list = [i for i, source in enumerate(source_list) if source
                         in SOURCE_SAVE_LIST]
    irrelevance_index_list = [i for i, source in enumerate(source_list) if
                              source in SOURCE_FILTER_LIST]
    # 来源保留与官网做并集，来源过滤与官网做差集，官网优先级更好，且保留过滤不可能有交集
    return (list(set(official_index_list) | set(source_index_list)),
            list(set(irrelevance_index_list) - set(official_index_list)))


def filter_tag(pattern, content):
    """关键词标注

    :param pattern: 正则匹配式
    :param content: 文本内容
    :return: tag 后的文本内容
    """
    if content:
        tag_word_list = [i.group() for i in re.finditer(pattern, content)]
        if tag_word_list != list():
            tag_word_list = list(set(tag_word_list))
            for word in tag_word_list:
                content = re.sub(word, FORMAT_BLACK_LIST_TAG.format(word),
                                 content)
        else:
            return None
    return content


def black_list_filter(items_list):
    """关键词过滤

    :param items_list: 单个条目列表
    :return: 过滤后的列表
    """
    query_type_list = [item['query_type'] for item in items_list]
    summary_list = [item['summary'] for item in items_list]
    filter_items_list = list()
    for i, summary in enumerate(summary_list):
        query_type = query_type_list[i]
        tag_summary = False
        if query_type in BLACK_LIST_MAP:
            if isinstance(BLACK_LIST_MAP[query_type], list):
                tag_summary = filter_tag(FORMAT_OR_REGEX.format('|'.join(
                                         BLACK_LIST_MAP[query_type])), summary)
        if tag_summary:
            items_list[i]['summary'] = tag_summary
            filter_items_list.append(items_list[i])
    return filter_items_list


def info_filter(items_list):
    """发起信息过滤

    :param items_list: 单个条目列表
    :return: 过滤后的字典列表
    """
    if items_list is not False:
        if items_list == list():
            return list()
    else:
        return False
    # TODO： 过滤部分分离逻辑
    # 只查一页的关键词目前不需要敏感词过滤
    if PAGE_DICT[items_list[0]['query_type']] == 1:
        return items_list
    page_items_list = items_list[:]
    remain_index_list = repetition_filter(page_items_list)
    if len(remain_index_list) == len(page_items_list):
        unique_items_list = items_list
    else:
        unique_items_list = [page_items_list[i] for i in remain_index_list]
    return_index_list, irrelevance_index_list = source_filter(unique_items_list)
    if len(return_index_list + irrelevance_index_list) == 0:
        check_items_list = unique_items_list
    else:
        check_items_list = [unique_items_list[i] for i in
                            range(len(unique_items_list)) if i not in
                            (return_index_list + irrelevance_index_list)]
    filter_items_list = black_list_filter(check_items_list)
    return_items_list = [unique_items_list[i] for i in
                         range(len(unique_items_list)) if i in
                         return_index_list]
    return filter_items_list + return_items_list


def fetch_direct_url(cache_url, proxies=None, headers=None):
    """获取快照真实链接

    :param cache_url: 快照链接
    :param proxies: 代理，同 Requests 参数要求
    :param headers: 请求头，同 Requests 参数要求
    :return: 快照跳转链接
    """
    response_list = url_request(cache_url, [dict()], proxies=proxies,
                                headers=headers)
    try:
        if response_list[0].status_code == requests.codes.ok:
            content = response_list[0].content.decode('utf-8', errors='ignore')
        elif response_list[0].status_code == 400:
            return None
        else:
            response_list[0].raise_for_status()
    except Exception as e:
        exception_raise(e, msg=cache_url)
    try:
        direct_url = re.search(REGEX_DIRECT_URL, content)
        if direct_url:
            if 'c.360webcache.com' in direct_url.group(1):
                return direct_url.group(1)
            else:
                return content
        else:
            return False
    except Exception as _:
        exception_raise(TypeError('fetch_direct_url() error {}'
                                  .format(cache_url)))


def fetch_cache_content(direct_url, proxies=None, headers=None):
    """获取快照真实内容

    :param direct_url: 快照跳转链接
    :param proxies: 代理，同 Requests 参数要求
    :param headers: 请求头，同 Requests 参数要求
    :return: 快照 html 内容
    """
    response_list = url_request(direct_url, [dict()], proxies=proxies,
                                headers=headers)
    try:
        if response_list[0].status_code == requests.codes.ok:
            return response_list[0].content.decode('utf-8', errors='ignore')
        elif response_list[0].status_code == 302:
            return None
        else:
            response_list[0].raise_for_status()
    except Exception as e:
        exception_raise(e, msg=direct_url)


def fetch_info_cache(items_list, proxies=None):
    """发起快照查询

    :param items_list: 敏感词过滤后的信息字典
    :param proxies: 代理，同 Requests 参数要求
    :return: 快照 html 内容列表
    """
    if items_list is not False:
        if items_list == list():
            return list()
    else:
        return False
    cache_url_list = [item['cached_url'] for item in items_list]
    cache_content_list = list()
    for cached_url in cache_url_list:
        if cached_url is None:
            cache_content_list.append(None)
            continue
        # 目前已知'百度知道'可以直接获取原网站链接，因此添加'so.com'过滤规则
        if 'so.com' not in cached_url:
            cache_content_list.append(FORMAT_REDIRECT_SCRIPT
                                      .format(cached_url, cached_url))
            continue
        direct_url = fetch_direct_url(cached_url, proxies=proxies,
                                      headers=SO_HEADERS)
        if direct_url is None:
            cache_content_list.append(None)
            continue
        elif direct_url[:4] != 'http':
            cache_content_list.append(direct_url)
            continue
        # TODO: 快照跳转到原网站的情况则不需要进行第二次请求
        elif direct_url is False:
            exception_raise(TypeError('cannot get direct_url')
                            .format(cached_url))
        cache_headers = copy.deepcopy(SO_HEADERS)
        cache_headers.update(Referer=cached_url)
        cache_content = fetch_cache_content(direct_url, proxies=proxies,
                                            headers=cache_headers)
        if cache_content is None:
            cache_content_list.append(None)
            continue
        cache_content_list.append(cache_content)
    return cache_content_list


def main(**kwargs):
    """主函数

    :param kwargs: 传入参数，proxies，data, page...
    :return: 内容字典
    """
    try:
        proxies = kwargs.get('proxies')
        data = kwargs.get('data')
        page = kwargs.get('page')
        # 接收参数
        info_dict = dict(query_type=data.keys()[0],
                         query_term=data[data.keys()[0]])
        # 下载页面
        page_dict = info_query(info_dict, page, proxies)
        if page_dict is False:
            exception_raise(TypeError('info_query() error'))
        # 页面解析
        # TODO: 最终结果进行过滤，不再利用 page 来进行判断
        items_list = info_parse(page_dict, page)
        if items_list is False:
            exception_raise(TypeError('info_parse() error'))
        # 精确匹配
        identical_list = info_identical(items_list)
        if identical_list is False:
            exception_raise(TypeError('info_identical() error'))
        # 过滤敏感词
        filter_list = info_filter(identical_list)
        if filter_list is False:
            exception_raise(TypeError('info_filter() error'))
        # return (dict(haosoukeywordinfo=filter_list))
        # 获取 html
        cache_list = fetch_info_cache(filter_list, proxies)
        if cache_list is False:
            exception_raise(TypeError('fetch_info_cache() error'))
        return (dict(haosoukeywordinfo=cache_list),
                dict(haosoukeywordinfo=filter_list))
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
    _IP_POOL = [
        'http://115.213.170.181:44391'
    ]
    proxies = {
        'http': _IP_POOL[0],
        'https': _IP_POOL[0],
    }
    task = dict(
        proxies=None,
        type='profile_retrieval',
        msg_no='',
        url='test.com',
        page=1,
        data={
            # 'name': '联金所',
            # 'name': '优酷',
            # 'name': '冯君贤',
            # 'id_num': '441827198609147000',
            # 'phone1': '13363446295',
            # 'phone2': '',
            # 'phone3': '',
            # 'company': '福耀集团(上海）汽车玻璃有限公司',
            # 'company': '上海基础工程集团有限公司',
            'company': '你我贷',
            # 'company': '深圳市棕榈滩露营用品有限公司'
            # 'company_phone1': '0532-58731555',
            # 'company_phone2': '075536648138',
            # 'company_phone3': '023-62889876',
            # 'spouse_name': '梁嘉雯',
            # 'spouse_id_card': '441802198407260000',
            # 'spouse_phone1': '13924413871',
            # 'spouse_phone2': '',
            # 'contact_phone1': '13631054187',
            # 'contact_phone2': '15972171851',
            # 'contact_phone3': '15992088600',
            # 'contact_phone4': '13826265800',
            # 'contact_phone5': '',
            # 'contact_phone6': '',
            # 'contact_phone7': '',
            # 'contact_phone8': '',
            # 'company_phone1_special': '075536648138',
            # 'company_phone2_special': '0532-58731555',
            # 'company_phone3_special': '',
            # 'company_search': '芜湖新兴铸管有限责任公司 电话',
            # 'company_search': '武安市诚利诚商贸有限公司 电话',
        },
    )
    print(start(**task))