#coding=utf-8
from shixin_spider import start as shixin_start
from zhixing_spider import start as zhixing_start


__intro__ = """分布式调用的爬虫测试"""


class Distributed(object):
    """分布式测试类"""

    @classmethod
    def shixin(cls):
        # 企业失信
        demo = dict(
            data={
                'name': '曹俊元',
                'id_num': '370822196712346118',
                'company': '上海彤新汽车销售服务有限公司',

                'spouse_name': '王风銮',
                'spouse_id_card': '370921196712343620',
                'spouse_company': '贵州四江顺发建筑劳务有限公司',
            }
        )
        results = shixin_start(**demo)
        # 数据繁多，建议设置断点调试
        print results
    # end

    @classmethod
    def zhixing(cls):
        # 法院被执行
        demo = dict(
            data={
                'name': '曹俊元',
                'id_num': '370822196712346118',
                'company': '上海彤新汽车销售服务有限公司',

                'spouse_name': '王风銮',
                'spouse_id_card': '370921196712343620',
                'spouse_company': '山东千百度投资担保有限公司',
            }
        )
        results = zhixing_start(**demo)
        # 数据繁多，建议设置断点调试
        print results
    # end

# class


if __name__ == '__main__':
    Distributed.shixin()