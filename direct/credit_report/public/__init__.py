#coding=utf-8
from pytesseract import image_to_string
from requests.utils import dict_from_cookiejar
from basic_request import Request
from code_desc import returnResult


from share_func import (
    getIP,
    recogImage,
    getUserAgent,
    clawLog,
    makeDirs

)

__all__=(
    'Request',
    'returnResult',
    'getIP',
    'getUserAgent',
    'clawLog',
    'makeDirs',
    'dict_from_cookiejar',
    'image_to_string',
)
