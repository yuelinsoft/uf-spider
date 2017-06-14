#coding=utf-8
from direct import(
    getPhoneAttr,
    phone_distribute,
    creditReportAPI,
    phonebookAPI,

)


__intro__ = """后台直接调用的爬虫测试"""

class Direct(object):
    """后台测试类"""

    @classmethod
    def phoneAttr(cls):
        # 获得手机属性
        phone_num = raw_input(u'请输入手机号:').strip()
        result = getPhoneAttr(phone_num)
        # 建议设置断点测试
        print result
    # end

    @classmethod
    def operator(cls):
        # 营运商
        phone_num = raw_input(u'请输入手机号:').strip()
        password  = raw_input(u'请输入服务密码：').strip()
        result = phone_distribute(phone_num, password)
        # 建议设置断点测试
        print result
    # end

    @classmethod
    def credit_report(cls):
        # 简版征信
        print u'授权查询，请谨慎测试'
        user_name = raw_input(u'请输入用户名:').strip()
        password = raw_input(u'请输入登陆密码:').strip()
        auth_pwd = raw_input(u'请输入身份验证码:').strip()

        user_name = user_name if user_name else 'creditReport'
        password = password if password else 'lianjinsuo'
        auth_pwd = auth_pwd if auth_pwd else 'abc123456'
        result = creditReportAPI(user_name, password, auth_pwd, debug=True)
        # 建议设置断点测试
        print result
    # end

    @classmethod
    def phone_book(cls):
        # 政府机构
        phonebookAPI()
    # end
# cls

if __name__ == '__main__':
    Direct.credit_report()