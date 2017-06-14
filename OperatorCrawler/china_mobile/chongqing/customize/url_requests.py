# -*- coding: utf-8 -*-
"""
    __author__ = LiJianBin

    For companyCredit

    This script can be used for http or https Requests.

    use method is the same as officially requests.

    Example:
        '>>> import urlRequest
        '>>> url = 'https://www.google.com'
        '>>> response = urlRequest.get(url)
        '>>> then you can print response.text for the html of the url preview.

"""


from __future__ import unicode_literals
import time
import random
from requests.sessions import Session
from requests.exceptions import SSLError, Timeout, ConnectionError, ProxyError
from uf_exception import IpRefused

User_Agent_List = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
       ]

HTTP_Status_Code = {

    100: '（继续） 请求者应当继续提出请求。 '
           '服务器返回此代码表示已收到请求的第一部分，正在等待其余部分。',
    101: '（切换协议） 请求者已要求服务器切换协议，服务器已确认并准备切换。',

    # 成功
    200: '（成功） 服务器已成功处理了请求。 通常，这表示服务器提供了请求的网页。 ',
    201: '（已创建） 请求成功并且服务器创建了新的资源。 ',
    202: '（已接受） 服务器已接受请求，但尚未处理。 ',
    203: '（非授权信息） 服务器已成功处理了请求，但返回的信息可能来自另一来源。 ',
    204: '（无内容） 服务器成功处理了请求，但没有返回任何内容。 ',
    205: '（重置内容） 服务器成功处理了请求，但没有返回任何内容。 ',
    206: '（部分内容） 服务器成功处理了部分 GET 请求。 ',

    # 重定向
    300: '（多种选择） 针对请求，服务器可执行多种操作。'
           '服务器可根据请求者(user_agent)选择一项操作，或提供操作列表供请求者选择。 ',
    301: '（永久移动） 请求的网页已永久移动到新位置。'
           '服务器返回此响应（对 GET 或 HEAD 请求的响应）时，会自动将请求者转到新位置。',
    302: '（临时移动） 服务器目前从不同位置的网页响应请求，'
           '但请求者应继续使用原有位置来进行以后的请求。',
    303: '（查看其他位置） 请求者应当对不同的位置使用单独的 GET 请求来检索响应时，'
           '服务器返回此代码。 ',
    304: '（未修改） 自从上次请求后，请求的网页未修改过。'
           '服务器返回此响应时，不会返回网页内容。 ',
    305: '（使用代理） 请求者只能使用代理访问请求的网页。 '
           '如果服务器返回此响应，还表示请求者应使用代理。 ',
    307: '（临时重定向） 服务器目前从不同位置的网页响应请求，'
           '但请求者应继续使用原有位置来进行以后的请求。 ',

    # 请求错误
    400: '（错误请求） 服务器不理解请求的语法。 ',
    401: '（未授权） 请求要求身份验证。 对于需要登录的网页，服务器可能返回此响应。 ',
    403: '（禁止） 服务器拒绝请求。 ',
    404: '（未找到） 服务器找不到请求的网页。 ',
    405: '（方法禁用） 禁用请求中指定的方法。 ',
    406: '（不接受） 无法使用请求的内容特性响应请求的网页。 ',
    407: '（需要代理授权） 此状态代码与 401（未授权）类似，'
           '但指定请求者应当授权使用代理。',
    408: '（请求超时） 服务器等候请求时发生超时。 ',
    409: '（冲突） 服务器在完成请求时发生冲突。 服务器必须在响应中包含有关冲突的信息。',
    410: '（已删除） 如果请求的资源已永久删除，服务器就会返回此响应。 ',
    411: '（需要有效长度） 服务器不接受不含有效内容长度标头字段的请求。 ',
    412: '（未满足前提条件） 服务器未满足请求者在请求中设置的其中一个前提条件。 ',
    413: '（请求实体过大） 服务器无法处理请求，因请求实体过大，超出服务器的处理能力。',
    414: '（请求的 URI 过长） 请求的 URI（通常为网址）过长，服务器无法处理。 ',
    415: '（不支持的媒体类型） 请求的格式不受请求页面的支持。 ',
    416: '（请求范围不符合要求） 如果页面无法提供请求的范围，则服务器会返回此状态代码。',
    417: '（未满足期望值） 服务器未满足”期望”请求标头字段的要求。 ',

    # 服务器错误
    500: '（服务器内部错误） 服务器遇到错误，无法完成请求。 ',
    501: '（尚未实施） 服务器不具备完成请求的功能。 '
           '例如，服务器无法识别请求方法时可能会返回此代码。 ',
    502: '（错误网关） 服务器作为网关或代理，从上游服务器收到无效响应。 ',
    503: '（服务不可用） 服务器目前无法使用（由于超载或停机维护）。通常，这只是暂时状态。',
    504: '（网关超时） 服务器作为网关或代理，但是没有及时从上游服务器收到请求。',
    505: '（HTTP 版本不受支持） 服务器不支持请求中所用的 HTTP 协议版本。'
}

_session = Session()

def get(url, params=None, sendTimes=3, **kwargs):
    """Sends a GET request. Returns :class:`Response` object.

    :param url: URL for requests
    :param params: (optional) Dictionary or bytes to be sent in the query
        string for the :class:`Request`.
    :param sendTimes: integer. times for send requests.
    :param kwargs: (headers, cookies, timeout, proxies, verify etc.)
    :rtype: requests.Response
    """

    return _request('GET', url=url, params=params, sendTimes=sendTimes,
                    **kwargs)

def post(url, data=None, json=None, sendTimes=3, **kwargs):
    """Sends a POST request. Returns :class:`Response` object.

    :param url: URL for requests
    :param data: Dictionary
    :param json: Dictionary
    :param sendTimes: integer. times for send requests.
    :param kwargs: (headers, cookies, timeout, proxies, verify etc.)
    :rtype: requests.Response
    """

    return _request('POST', url=url, data=data, json=json, sendTimes=sendTimes,
                    **kwargs)

def _request(method, url, sendTimes=3, **kwargs):
    """Constructs a :class:`Request <Request>`, prepares it and sends it.
    Returns :class:`Response <Response>` object.

    :param method: 'get' or 'post'
    :param url: URL for requests
    :param sendTimes: integer. times for send requests.
    :param params: (optional) Dictionary or bytes to be sent in the query
        string for the :class:`Request`.
    :param data: (optional) Dictionary, bytes, or file-like object to send
        in the body of the :class:`Request`.
    :param json: (optional) json to send in the body of the
        :class:`Request`.
    :param headers: (optional) Dictionary of HTTP Headers to send with the
        :class:`Request`.
    :param cookies: (optional) Dict or CookieJar object to send with the
        :class:`Request`.
    :param timeout: (optional) How long to wait for the server to send
        data before giving up, as a float, or a :ref:`(connect timeout,
        read timeout) <timeouts>` tuple.
    :type timeout: float or tuple
    :param proxies: (optional) Dictionary mapping protocol or protocol and
        hostname to the URL of the proxy.
    :param verify: (optional) whether the SSL cert will be verified.
        A CA_BUNDLE path can also be provided. Defaults to ``True``.
    :rtype: requests.Response
    """

    try:
        if 'timeout' not in kwargs or kwargs['timeout'] > 30:
            kwargs['timeout'] = 30

        response = _session.request(method=method, url=url, **kwargs)

        status_code = response.status_code
        if status_code == 200:

            return response
        else:
            message = '<Response [%s]>: %s' % (status_code,
                                                HTTP_Status_Code[status_code])

            raise IpRefused(message.encode('utf-8'))

    except Exception as request_exception:
        # sendTimes = sendTimes
        sendTimes -= 1
        if sendTimes < 1:
            raise
        else:
            time.sleep(random.uniform(0, 1))
            if isinstance(request_exception, Timeout):

                return _request(method, url, sendTimes=sendTimes, **kwargs)

            elif isinstance(request_exception, SSLError):

                kwargs['verify'] = False
                return _request(method, url, sendTimes=sendTimes, **kwargs)

            elif isinstance(request_exception, ProxyError):

                raise IpRefused(request_exception.message)

            elif isinstance(request_exception, ConnectionError):

                return _request(method, url, sendTimes=sendTimes, **kwargs)

            else:

                return _request(method, url, sendTimes=sendTimes, **kwargs)

def random_userAgent():
    """random userAgent"""

    i = random.randrange(0, len(User_Agent_List))

    return User_Agent_List[i]