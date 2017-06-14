#coding=utf-8
import re
import json
import time
from math import ceil
from lxml import etree
import depend.table as Table
from depend.assist_sql import Search

from public import (
    dbInsert,
    getIp,
    getUserAgent,
    Request,
    recogImage,
    dict_from_cookiejar
)



class ShiXinSpider(object):
    """企业失信-实时查询-spider"""

    def __init__(self, name, card_num):
        self.headers = {
            'Referer': '',
            'X-Forwarded-For': getIp(),
            'User-Agent':  getUserAgent(),
            'Accept-Language': 'zh-CN,zh;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'shixin.court.gov.cn',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        }
        self.cookies = dict()           # 全局cookies
        self.name = name                # 个人姓名/公司名
        self.card_num = card_num        # 身份证号/企业号
        self.id_seq = list()            # 查询结果id序列
        self.valid_items = list()       # 有效记录
        self.invalid_items = list()     # 无效记录
    # end

    def getCookies(self):
        """ 获取cookies
        :return: dict obj/False　"""
        def visitSys():
            url = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url':url, 'headers': self.headers}
            response = Request.basic(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                # invoke next process
                return getSessionID()
            else:
                return False
        # def

        def getSessionID():
            url = 'http://shixin.court.gov.cn/image.jsp'
            self.headers['Referer'] = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url': url, 'cookies': self.cookies, 'headers': self.headers}
            response = Request.basic(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
                #invoke next process
                return getONEAPM()
            else:
                return False
        # def

        def getONEAPM():
            url = 'http://shixin.court.gov.cn/visit.do'
            self.headers['Referer'] = 'http://shixin.court.gov.cn/'
            options = {'method': 'get', 'url': url, 'cookies': self.cookies, 'headers': self.headers}
            response = Request.basic(options)
            if response:
                self.cookies.update(dict_from_cookiejar(response.cookies))
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
        result = time.ctime().split()
        url =   'http://shixin.court.gov.cn/image.jsp?' \
                'date={0}%20{1}%20{2}%20{3}%20{4}%20GMT' \
                '+0800%20(%E4%B8%AD%E5%9B%BD%E6%A0%87%E5%87%86%E6%97%B6%E9%97%B4)'\
                .format(result[0], result[1], result[2], result[4], result[3])
        self.headers['Accept'] = 'image/webp,image/*,*/*;q=0.8'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'
        options = {'method': 'get', 'url': url, 'cookies': self.cookies, 'headers': self.headers}
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
            return self.getCode( re_num) if re_num > 0 else False
    # end

    def searchByCardNumAndName(self, pw_code, re_num=2):
        """ 进行查询
        :param pw_code: 识别后的验证码
        :param re_num: 重复次数
        :return: dict(page_num=page_num, pw_code=pw_code) """
        form = {
            'pProvince': '0',
            'pCode': pw_code,
            'pName': self.name,
            'pCardNum': self.card_num
        }
        url = 'http://shixin.court.gov.cn/findd'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'
        options = {'method': 'post', 'url': url, 'form': form,
                   'cookies': self.cookies, 'headers': self.headers}

        response = Request.basic(options)
        if response:
            page_num = 0
            selector = etree.HTML(response.content)
            text = selector.xpath('//div[@id="ResultlistBlock"]/div/text()')
            text = ''.join(text).replace('\n','').replace('\t','').encode('utf-8')
            try:
                tr_num = int(re.search('共(\d+)', text).group(1))  #记录总数
            except AttributeError:
                re_num -= 1
                pw_code = self.getCode()
                return self.searchByCardNumAndName(pw_code, re_num) if re_num > 0 else False
            else:
                if tr_num > 0:
                    page_num = int(ceil((tr_num)/10.0)) # 总页数
                    sys_ids = self.findIDs(selector)
                    self.id_seq.extend(sys_ids)
                return dict(page_num=page_num, pw_code=pw_code)
    # end

    def findIDs(self, selector):
        """ :param selector:
        :return: list　"""
        trs = selector.xpath('//table[@id="Resultlist"]/tbody/tr')[1:]
        return [tr.xpath('td[5]/a/@id')[0] for tr in trs]
    # end

    def changePage(self, pw_code, page_i):
        """ 请求第i页并提取当前页的所有id
        :param pw_code: 识别后的验证码
        :param page_i: 第i页
        :return: None　"""
        form = {
            'pProvince': '0',
            'pCode':  pw_code,
            'currentPage':page_i,
            'pName':  self.name,
            'pCardNum': self.card_num,
        }
        url = 'http://shixin.court.gov.cn/findd'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/findd'
        options = {'method':'post', 'url':url, 'form':form,
                   'cookies':self.cookies, 'headers':self.headers}

        response = Request.basic(options)
        if response:
            selector = etree.HTML(response.content)
            sys_ids = self.findIDs(selector)
            self.id_seq.extend(sys_ids)
    # end

    def saveErrID(self, sys_id, err_type):
        """:param sys_id: 单个id或者list,tuple
        :param err_type:
        :return:None　"""
        if err_type not in (1, 2, 3):
            raise ValueError(u'错误类型范围不在定义范围')

        if isinstance(sys_id, (list, tuple)):
            for i in sys_id:
                error = dict(sys_id = i, err_type = err_type)
                self.invalid_items.append(error)
        else:
            error = dict(sys_id = sys_id, err_type = err_type)
            self.invalid_items.append(error)
    # end

    def getJson(self, sys_id, pw_code, re_num=2):
        """  获得sys_id对应的信息
        :param pw_code: 识别后的验证码
        :param re_num: 重复次数
        :return: None　"""
        params = {'id':sys_id, 'pCode':pw_code}
        url = 'http://shixin.court.gov.cn/findDetai'
        self.headers['Referer'] = 'http://shixin.court.gov.cn/'

        options = {'method': 'get', 'params':params, 'url': url,
                   'cookies': self.cookies, 'headers': self.headers, 'timeout': 2 }
        response = Request.basic(options)
        if response and response.status_code not in (520, 500) and len(response.text):
            try:
                item = json.loads(response.text, encoding='utf-8')
            except (ValueError, Exception):
                self.saveErrID(sys_id, 3)
            else:
                result = dict()
                for k, v in item.items():
                    if k in Table.KEY_CONVERT_VALID.keys():
                        key = Table.KEY_CONVERT_VALID[k]
                        result[key] = v
                # 'businessEntity'存在判定为公司，否则为个人
                result['flag']  = 1 if 'businessEntity' in item.keys() else 0
                self.valid_items.append(result)
        else:
            re_num -= 1
            return self.getJson(sys_id, pw_code, re_num) if re_num > 0 else False
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
                     Table.KEY_CONVERT_INVALID,
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
    spider = ShiXinSpider(name, card_num)
    cookie = spider.getCookies()
    if not cookie:
        raise ValueError(u'请求失败，无法获得cookies')

    pw_code = spider.getCode()
    if not pw_code:
        raise ValueError(u'请求失败，无法获得图片验证码')

    result = spider.searchByCardNumAndName(pw_code)
    if not result:
        raise ValueError(u'请求失败，无法查找')

    # 迭代页面
    if result['page_num'] > 1:
        for page_i in range(2, result['page_num']+1):
            spider.changePage(result['pw_code'], page_i)
    # 迭代id
    if spider.id_seq:
        for sys_id in spider.id_seq:
            spider.getJson(sys_id , result['pw_code'])

    return spider.valid_items
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

def shixinSearch(name, relation_key, card_num=''):
    """ 逻辑查询接口
    :param name: 姓名/公司
    :param relation_key: 关系
    :param card_num: 重复次数
    :param debug: True/False, True时直接查库
    :return: 参考return """

    status, data = 4444, list()
    relation_ship = relation(relation_key)

    data = list(Search.query(name, card_num))  # 查库
    try:
        pass
        # temp = realSearch(name, card_num)  # 实查
    except Exception as ex:
        print u'失信实时查询异常,ex_info:{0}'.format(ex)
    else:
        pass
        # data.extend(temp)  # 合并
    finally:
        # 2000查询成功并有数据,2100查询成功但没数据
        status = 2000 if len(data) else 2100
        return {
            'name': name,
            'id_num': card_num,
            'status': status,
            'info': tuple(data),
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
        borrower = shixinSearch(name, 1000, id_num)
        result.append(borrower)
    if company:
        borrower_company = shixinSearch(company, 3000)
        result.append(borrower_company)
    if spouse_name and spouse_id_num:
        spouser = shixinSearch(spouse_name, 1100, spouse_id_num)
        result.append(spouser)
    if spouse_company:
        spouse_company = shixinSearch(spouse_company, 3300)
        result.append(spouse_company)
    return result
# end


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






