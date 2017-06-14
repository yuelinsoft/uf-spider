#coding=utf-8
import time
import random
from requests import request
from requests.exceptions import (
    ProxyError,
    SSLError,
    Timeout,
    ReadTimeout,
    ConnectTimeout,
    RequestException
)
from requests.packages.urllib3 import disable_warnings
from requests.packages.urllib3.exceptions import InsecureRequestWarning
disable_warnings(InsecureRequestWarning)


class Request(object):

    proxies = None  # 代理

    @classmethod
    def basic(cls, options, resend_times=1):
        """ 根据参数完成request请求，成功返回response对象, 否则False
        :param options: dict请求参数
        :param resend_times: 重发次数
        :return: response对象或False
        example:
        options = {
            'method':'get',
            'url':'http://www.eprc.com.hk/EprcWeb/multi/transaction/login.do',
            'form':None,
            'params':None,
            'cookies':None,
            'headers':headers,
        }
        response = Request.basic(options)
        """
        keys = options.keys()
        options['timeout'] = options['timeout'] if 'timeout' in keys else 10
        try:
            response = request(
                options['method'],
                options['url'],
                timeout = options['timeout'],
                proxies = Request.proxies,
                verify = options['verify'] if 'verify' in keys else False,
                data = options['form'] if 'form' in keys else None,
                params = options['params'] if 'params' in keys else None,
                cookies = options['cookies'] if 'cookies' in keys else None,
                headers = options['headers'] if 'headers' in keys else None,
                stream =  options['stream'] if  'stream' in keys else False,
                allow_redirects= options['allow_redirects'] if 'allow_redirects' in keys else False
            )
        except (ConnectTimeout, ReadTimeout, Timeout) as ex:
            # 超时随机挂起重传
            print 'watch out, timeout:',ex
            if resend_times > 0:
                time.sleep(random.uniform(0, 1))
                options['timeout'] += 1
                return cls.basic(options, resend_times-1)
            else:
                return False

        except ProxyError as ex:
            # 代理异常设置为None挂起重传
            print 'watch out, proxyerror:',ex
            if resend_times > 0:
                time.sleep(random.uniform(0, 1))
                cls.proxies = None
                return cls.basic(options, resend_times-1)
            else:
                return False

        except SSLError as ex:
            # 认证异常设置为False挂起重传
            print 'watch out, SSLerror:',ex
            if resend_times > 0:
                time.sleep(random.uniform(0, 1))
                options['verify'] = False
                return cls.basic(options, resend_times-1)
            else:
                return False

        except (RequestException, Exception) as ex:
             # 其他异常挂起重传
            print 'watch out, other error:',ex
            if resend_times > 0:
                time.sleep(random.uniform(0, 1))
                return cls.basic(options, resend_times-1)
            else:
                print u'危险:请求参数为{0}存在未分类异常,错误为{1}'.format(options, ex)
                return False
        else:
            return response
    # end
# class


def _demo(phone_num):
    """ 使用Request类的demo
    :param phone_num:
    :return:
    """
    Request.proxies = {'http':'192.168.10.40', 'https':'192.168.10.40:8888'}
    params = {'tel': phone_num}
    options = {
        'method':'get',
        'url': 'https://tcc.taobao.com/cc/json/mobile_tel_segment.htm',
        'params': params,
    }
    response = Request.basic(options)
    if response:
        print response.text
# end


if __name__ == '__main__':
    _demo('15850781443')