"""
public-space
"""
from __future__ import absolute_import
from requests.utils import dict_from_cookiejar
from .basic_request import Request
from .code_desc import return_result

from .share_func import (
    get_ip,
    get_timestamp,
    recog_image,
    get_UserAgent,
    claw_log,
    make_dirs,
    password_encryption_based_ras
)

__all__ = (
    'Request',
    'return_result',
    'dbInsert',
    'get_ip',
    'get_timestamp',
    'recog_image',
    'get_UserAgent',
    'claw_log',
    'make_dirs',
    'image_to_string',
    'getDBConnection',
    'dict_from_cookiejar',
    'password_encryption_based_ras',

)
