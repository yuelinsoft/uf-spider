#coding=utf-8
import time
import random
from requests import request
from share_func import clawLog
from requests.exceptions import (
    ProxyError,
    SSLError,
    Timeout,
    ReadTimeout,
    ConnectTimeout,
    TooManyRedirects,
    HTTPError,
    ConnectionError,
    RequestException,
    InvalidURL
)
RESTART_LIST = [ ProxyError, Timeout, ReadTimeout, ConnectTimeout, HTTPError]

SHUTDOWN_LIST = [SSLError, TooManyRedirects, InvalidURL,ConnectionError,
                 ValueError]

from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)

class Request(object):

    #代理设置为类属性
    proxies=None

    # 定义一个异常方法，将捕获的异常作为参数传给error
    @staticmethod
    def exception_raise(error, msg='', code=None):
        """
        :error是一个异常类
        :param error:异常类
        :param msg:自定义异常信息，不填为空
        :param code:异常代码（100：重新爬取，101：停止爬取）
        :return:
        """
        error.uf_msg = '[{0}]<{1}>'.format(type(error), msg)
        if not code:
            if type(error) in RESTART_LIST:
                error.uf_errno = 100
            elif type(error) in SHUTDOWN_LIST:
                error.uf_errno = 101
            else:
                error.uf_errno = 101

        else:
            error.uf_errno = 101
        print error.uf_errno
        print error.uf_msg
        raise error

    @classmethod
    def basic(cls,options,resend_times=2):
        """
        根据参数完成request请求，成功返回response对象,否则False
        :param options: dict
        :param resend_times:
        :return:
        """
        keys=options.keys()
        options['timeout']=options['timeout'] if 'timeout' in keys else 10
        try:
            response=request(
                options['method'],
                options['url'],
                timeout=options['timeout'],
                proxies=Request.proxies,
                verify=options['verify'] if 'verify' in keys else False,
                data=options['form'] if 'form' in keys else None,
                cookies=options['cookies'] if 'cookies' in keys else None,
                headers=options['headers'] if 'headers' in keys else None,
                stream=options['stream'] if 'stream' in keys else False,
            )
            return response

        except (ConnectTimeout,ReadTimeout,Timeout) as e:
            #超时随机挂起重传
            Request.exception_raise(e,msg=options['url'])


        except (ConnectionError,ProxyError) as e:
            Request.exception_raise(e,msg=options['url'])

        except (SSLError) as e:
            Request.exception_raise(e,msg=options['url'])

        #异常代码为101的异常
        except (InvalidURL) as e:
            Request.exception_raise(e,msg=options['url'])

        except  TooManyRedirects as e:
            Request.exception_raise(e,msg=options['url'])

        except ValueError as e:
            Request.exception_raise(e, msg=options['url'])

        except (RequestException, Exception) as e:
            Request.exception_raise(e, msg=options['url'])

def _demo(phone_num):
    """
    测试使用Request类发送请求
    :param phone_num:
    :return:
    """
    Request.proxies={'https':'192.168.10.40:8888'}
    params={'tel':phone_num}
    options={
        'method':'get',
        'url':'https://www.baidu.com/',
        'timeout':5,
        'params':params,

        'headers':{
        'Accept-Language': 'zh-CN',
        'Connection': 'keep-alive',
        'Accept-Encoding': 'gzip, deflate',
        'Accept': 'text/html, application/xhtml+xml, image/jxr, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.59 Safari/537.36'
    }

    }
    response=Request.basic(options)
    if response:
        print response.text
    else:
        print "Not things"
#end

if __name__=="__main__":
    _demo('7878')




























