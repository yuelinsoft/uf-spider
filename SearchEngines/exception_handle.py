#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

"""
    exception_handle
    ~~~~~~~~~

    异常交互封装，添加错误操作码与错误信息

    :copyright: (c) 2017 by cds@uf-club.
    :license: MIT, see LICENSE for more details.
"""

__versions__ = '5.0.1'

from _ssl import SSLError as SSLError2
from requests.exceptions import (ProxyError, SSLError, Timeout, ReadTimeout,
                                 ConnectTimeout, TooManyRedirects, InvalidURL,
                                 HTTPError, ConnectionError)

RESTART_LIST = [Timeout, ReadTimeout, ConnectTimeout, HTTPError, SSLError,
                ConnectionError, SSLError2, ValueError]
SHUTDOWN_LIST = [TooManyRedirects, InvalidURL, KeyError, TypeError]
PROXY_LIST = [ProxyError]


def exception_raise(error, msg='', code=None):
    # type: (object, object, object) -> object
    """输入一个（系统返回）异常类，添加信息后重新升起异常

    :param error: 异常类
    :param msg: 自定义异常信息，不填则为空
    :param code: 异常代码（100: 重新爬取，101: 停止爬取），不填则自动分类
    :return:
    """
    error.uf_msg = '[{0}]<{1}>'.format(type(error), msg)
    if not code:
        if type(error) in RESTART_LIST:
            error.uf_errno = 100
        elif type(error) in SHUTDOWN_LIST:
            error.uf_errno = 101
        elif type(error) in PROXY_LIST:
            error.uf_errno = 102
    else:
        error.uf_errno = code
    raise error