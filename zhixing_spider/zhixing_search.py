#coding=utf-8
import re
import json
import random
from math import ceil
from lxml import etree
import depend.table as Table
from depend.assist_sql import Search

from .public import (
    Request,
    getUserAgent,
    getIp,
    recogImage,
    dbInsert,
    dict_from_cookiejar
)


_timeout = 5

class ZhiXingSpider(object):
    """法院被执行-实时查询-spider"""

    def __init__(self, name, card_num):
        self.headers = {
            'Referer': '',
            'User-Agent': getUserAgent(),
            'Connection': 'keep-alive',
            'Host': 'zhixing.court.gov.cn',
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'X-Forwarded-For': getIp(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.cookies = dict()           # "全局"cookies
        self.name = name                # 个人姓名/公司名
        self.card_num = card_num        # 身份证号/企业号
        self.id_seq = list()            # 查询结果id序列
        self.valid_items = list()       # 有效id
        self.invalid_items = list()     # 无效/出错id
    # end

    def getCookies(self):
        """ 获取cookies流程（嵌套函数）
        :return: dict obj/False """
        def visitSys():
            url = 'http://zhixing.court.gov.cn/search/'
            options = {'method':'get', 'url':url, 'headers':self.headers}

            response = Request.basic(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                # invoke next process
                return getSessionID()
            else:
                return False
        # def

        def getSessionID():
            url_one = 'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?87'
            self.headers['Referer'] = 'http://zhixing.court.gov.cn/'
            options_one = {'method':'get', 'url':url_one, 'cookies':self.cookies, 'headers':self.headers}

            response =  Request.basic(options_one)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                #invoke next process
                return self.cookies
            else:
                return False
        # def
        return visitSys()
    # end

    def getCode(self, re_num=2):
        """获取验证码[全为数字], 并进行识别
        :param re_num: 重复次数
        :return: 识别结果/False　"""
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        url =  'http://zhixing.court.gov.cn/search/security/jcaptcha.jpg?' + str(random.randint(0,99))
        options = {'method':'get', 'url':url, 'cookies':self.cookies, 'headers':self.headers}

        response = Request.basic(options)
        if response and len(response.text):
            self.cookies.update(dict_from_cookiejar(response.cookies))
            pw_code = recogImage(response.content)
            if pw_code:
                return pw_code
            else:
                re_num -= 1
                return self.getCode(re_num) if re_num > 0 else False
        else:
            re_num -= 1
            return self.getCode(re_num) if re_num > 0 else False
    # end

    def searchByCardNum(self, re_num=2):
        """ 进行查询
        :param pw_code: 识别后的验证码
        :param re_num: 重复次数
        :return: 总页数 """
        pw_code = self.getCode()
        if not pw_code:
            re_num -= 1
            return self.searchByCardNum(re_num) if re_num > 0 else False

        form = {
            'searchCourtName': '全国法院（包含地方各级法院）',
            'selectCourtId': '1',
            'selectCourtArrange': '1',
            'pname': self.name,
            'cardNum': self.card_num,
            'j_captcha': pw_code
        }
        url = 'http://zhixing.court.gov.cn/search/newsearch'
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method':'post', 'url':url, 'form':form, 'timeout':_timeout,
                   'cookies':self.cookies, 'headers':self.headers}

        response = Request.basic(options, resend_times=0)
        if response:
            checkout = self.checkOut(response.text)
            if not checkout:
                re_num -= 1
                return self.searchByCardNum(re_num)if re_num > 0 else False
            else:
                page_num = 0
                selector = etree.HTML(response.text)
                text = selector.xpath('//div[@id="ResultlistBlock"]/div/text()')
                text = ''.join(text).replace('\n','').replace('\t','').encode('utf-8')
                tr_num = int(re.search('共(\d+)', text).group(1))
                if tr_num > 0:
                    page_num = int(ceil((tr_num)/10.0))
                    sys_ids = self.findIDs(selector)
                    self.id_seq.extend(sys_ids)
                return page_num
    # end

    def findIDs(self, selector):
        """ :param selector:
        :return: list　"""
        trs = selector.xpath('//table[@id="Resultlist"]/tbody/tr')[1:]
        return [tr.xpath('td[5]/a/@id')[0] for tr in trs]
    # end

    def changePage(self, page_i, re_num=2):
        """ 请求第i页并提取当前页的所有id
        :param page_i: 第i页
       :param pw_code: 重复次数
        :return: None　"""
        pw_code = self.getCode()
        if not pw_code:
            re_num -= 1
            return self.changePage(page_i, re_num) if re_num > 0 else False

        form = {
            'currentPage': page_i,
            'selectCourtId': '1',
            'selectCourtArrange': '1',
            'pname': self.name,
            'cardNum': self.card_num
        }
        url = 'http://zhixing.court.gov.cn/search/newsearch?j_captcha=' + pw_code
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method':'post', 'url':url, 'form':form, 'timeout':_timeout,
                   'cookies': self.cookies, 'headers':self.headers}

        response = Request.basic(options, resend_times=0)
        if response:
            checkout = self.checkOut(response.text)
            if not checkout:
                re_num -= 1
                return self.changePage(page_i, re_num) if re_num > 0 else False
            else:
                selector = etree.HTML(response.text)
                sys_ids = self.findIDs(selector)
                self.id_seq.extend(sys_ids)
        else:
            re_num -= 1
            return self.changePage(page_i, re_num) if re_num > 0 else False
    # end

    def checkOut(self, text):
        """ 通过页面返回内容检查验证码是否出错,
        正确返回True,否则返回False
        :param text:response.text
        :return:True/False
        """
        selector = etree.HTML(text)
        title = selector.xpath('//title/text()')[0]
        checkout = re.match('验证码出现错误', title.encode('utf-8'))
        return False if checkout else True
    # end

    def saveErrID(self, sys_id, err_type):
        """ 保存出错的id,和对应的错误类型
        1位请求错误/2为超时/3为未知错误
        :param sys_id: id
        :param err_type: 1/2/3
        :return: None
        """
        if err_type not in (1,2,3):
            raise ValueError
        err_item = dict(sys_id=sys_id,err_type=err_type)
        self.invalid_items.append(err_item)
        return False
    # end

    def getJson(self, sys_id, re_num=2):
        """  获得sys_id对应的信息
        :param sys_id: 记录对应的id
        :param re_num: 重复次数
        :return: None　"""
        pw_code = self.getCode()
        if not pw_code:
            re_num -= 1
            return self.getJson(sys_id, re_num) if re_num > 0 else self.saveErrID(sys_id, 1)

        params = {'id':sys_id, 'j_captcha':pw_code}
        url = 'http://zhixing.court.gov.cn/search/newdetail'
        self.headers['Referer'] = 'http://zhixing.court.gov.cn/search/'
        options = {'method': 'get', 'params':params, 'url': url, 'timeout':_timeout,
                   'cookies': self.cookies, 'headers': self.headers}

        response = Request.basic(options, resend_times=0)
        if response and len(response.text) > 10:
            try:
                item = json.loads(response.text, encoding='utf-8')
            except (ValueError,Exception):
                self.saveErrID(sys_id, 3)
            else:
                result = dict()
                for k, v in item.items():
                    if k in Table.KEY_COLUMN.keys():
                        key = Table.KEY_COLUMN[k]
                        result[key] = v
                self.valid_items.append(result)
        else:
            re_num -= 1
            return self.getJson(sys_id, re_num) if re_num > 0 else self.saveErrID(sys_id, 3)
    # end

    def saveItems(self):
        """ 将结果保存到数据库,以便测试字段的一致性
        :return: 结果统计信息 """
        valid_num  = len(self.valid_items)
        invalid_num = len(self.invalid_items)

        if valid_num:
            dbInsert(Table.TABEL_NAME_1,
                     Table.COLUMN_VALID,
                     self.valid_items
            )
        if invalid_num:
            dbInsert(Table.TABLE_NAME_2,
                     Table.COLUMN_INVALID,
                     self.invalid_items
            )
        return u'完成入库：有效信息{0}，错误信息{1}'.format(valid_num, invalid_num)
    # end

# class


def realSearch(name, card_num=''):
    """ 实时查询接口
    :param name: 姓名/公司名称
    :param card_num: 证件号[公司为空]
    :return: ({},....)/()
    """
    spider = ZhiXingSpider(name, card_num)
    spider.getCookies()
    page_num = spider.searchByCardNum()

    if page_num > 1:
        for page in range(2, page_num+1):
            spider.changePage(page)

    if spider.id_seq:
        for sys_id in spider.id_seq:
            spider.getJson(sys_id)

    # result = spider.saveItems()
    # clawLog(spider.id_seq, result)

    return tuple(spider.valid_items)
# end


# 关系的转换
def relation(key):
    convert = {
        1000: u'个人',
        1100: u'配偶',
        3000: u'借款人就职公司',
        3300: u'配偶就职公司'
    }
    if key in convert.keys():
        return convert[key]
    else:
        raise ValueError(u'Error: relation_key')
# end

def zhixingSearch(name, relation_key, card_num='', debug=True):
    """ 逻辑查询接口
    :param name: 姓名/公司
    :param relation_key: 关系
    :param card_num: 重复次数
    :param debug: True/False, True时直接查库
    :return: 参考return """
    status, data = 4444, tuple()
    relation_ship = relation(relation_key)
    try:
        if debug == True:
            data = Search.query(name, card_num)
        else:
            data = realSearch(name, card_num)
    except Exception as ex:
        print u'执行查询异常,ex_info:{0}'.format(ex)
    else:
        # 2000查询成功并有数据,2100查询成功但没数据
        status = 2000 if len(data) else 2100
    finally:
        return {
            'name': name,
            'id_num': card_num,
            'status': status,
            'info': data,
            'relationship': relation_ship
        }
# end


def start(**kwargs):
    """ 分布式接入接口
    :return: 参考__intro__ """
    data = kwargs.get('data')
    name = data.get('name')               # 借款人姓名
    id_num =  data.get('id_num')          # 借款人身份证号
    company = data.get('company')         # 借款人就职公司

    spouse_name = data.get('spouse_name')         # 配偶姓名
    spouse_id_num =  data.get('spouse_id_card')   # 配偶身份证号
    spouse_company = data.get('spouse_company')   # 配偶就职公司

    result = list()
    if name and id_num:
        borrower = zhixingSearch(name, 1000, id_num)
        result.append(borrower)
    if company:
        borrower_company = zhixingSearch(company, 3000)
        result.append(borrower_company)
    if spouse_name and spouse_id_num:
        spouser = zhixingSearch(spouse_name, 1100, spouse_id_num)
        result.append(spouser)
    if spouse_company:
        spouse_company = zhixingSearch(spouse_company, 3300)
        result.append(spouse_company)
    return result
# end


if __name__ == '__main__':
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
    results = start(**demo)


__intro__ = """
返回格式:
[ {
    'name': name,
    'id_num': card_num,
    'status': status,
    'info': data,
    'relationship': relationship_desc
  },
 ...
]

含义简介:
name: 字符串
id_num: 字符串
status：整数
    2000 [查询成功内容不为空]
    2100 [查询成功但内容为空]
    4444 [查询失败]
info: 字典元组/空元祖
relationship: 字符串
    u'个人',
    u'配偶',
    u'借款人就职公司',
    u'配偶就职公司'
"""