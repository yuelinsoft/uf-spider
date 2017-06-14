# -*- coding: utf-8 -*-
"""
    自定义异常模块

    根异常： UfException（继承Exception）

    次级异常：
        RequestError： requests请求异常;

        ParametersError： 参数名异常;

        ServiceError: 为开通服务省份异常;

        每个次级异常都继承根异常，并需要添加 uf_errno 和 credit_status 属性。

        每添加一个新的状态码，需要在 UfException 类下声明，如例。

    Excample：

        from uf_exception import RequestError # (requests请求发出的异常)

        # 在分布式入口的 start 函数最外层 try
        def start(**kwargs):
            try：

                raise RequestError(“请求异常”) # 主程序部分

            except UfException as err：  # 判断该异常是否属于 UfException

                err.uf_msg = err.message    # 将异常信息保存到 uf_msg 里面
                # etc

                raise err

            except Exception as err:    # 捕获脚本其他非 UfException 里的异常

                err.uf_msg = err.message    # 将异常信息保存到 uf_msg 里面
                # etc

                raise err
"""


class UfException(Exception):
    """Base-class for all exception raised by this module."""

    uf_errno = 100
    status_code = 4000    # 网络异常


class RequestError(UfException):
    """RequestsException."""

    uf_errno = 100
    status_code = 4000    # 网络请求错误


class ParameterError(UfException):
    """Parameter is not valid"""

    uf_errno = 101
    status_code = 4400    # 参数错误


class ServiceError(UfException):
    """The company_city have not service"""

    uf_errno = 101
    status_code = 4444    # 暂未提供查询服务

class IpRefused(UfException):
    """need to change proxies"""

    uf_errno = 102
    status_code = 4000  # IP被禁止

class SuccessNoData(UfException):
    """Success, but not data"""

    uf_errno = 102
    status_code = 2100  # 成功无数据

class CaptchaFailed(UfException):
    """Captcha OCR failed"""

    uf_errno = 102
    status_code = 4200  # 验证码识别失败

