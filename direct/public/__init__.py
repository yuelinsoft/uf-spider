"""
public-space
"""
from __future__ import absolute_import
from pytesseract import image_to_string
from requests.utils import dict_from_cookiejar
from .basic_request import Request
from .code_desc import returnResult
from .db_insert import dbInsert, getDBConnection

from .share_func import (
    getIp,
    getTimestamp,
    recogImage,
    getUserAgent,
    clawLog,
    makeDirs
)

__all__ = (
    'Request',
    'returnResult',
    'dbInsert',
    'getIp',
    'getTimestamp',
    'recogImage',
    'getUserAgent',
    'clawLog',
    'makeDirs',
    'image_to_string',
    'getDBConnection',
    'dict_from_cookiejar'

)
