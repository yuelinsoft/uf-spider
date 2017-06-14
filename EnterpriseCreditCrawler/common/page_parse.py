# -*- coding: utf-8 -*-
"""
    __author__ = 'LiJianBin'

    just be used for CompanyCredit

    this script can be use to parse HTML content or json(maybe can't.(-*__*-))

"""

from __future__ import unicode_literals
import re

_tableNameList = ['qyxx_basicinfo', 'qyxx_s_h', 'qyxx_b_c', 'qyxx_member',
                  'qyxx_branch', 'qyxx_mortgage_basic', 'qyxx_pledge',
                  'qyxx_adm_punishment', 'qyxx_abnormal', 'qyxx_black_info',
                  'qyxx_spot_check',
                  'qyxx_stock_freeze', 'qyxx_stockholder_change',
                  'qyxx_c_mortgage', 'qyxx_s_creditor', 'qyxx_mortgage'
                  ]

all_execute = [
        'basicinfo_execute', 's_h_execute', 'b_c_execute', 'member_execute',
        'branch_execute', 'mortgage_basic_execute', 'pledge_execute',
        'adm_punishment_execute', 'abnormal_execute',
        'black_info_execute', 'spot_check_execute',
        'stock_freeze_execute', 'stockholder_change_execute',
        'c_mortgage_execute', 's_creditor_execute', 'mortgage_execute'
    ]

class CreditInfo(object):
    """
        Function of this class:
            1、Initialize all table values.

            2、save all of table_results to the _data.

            3、some function to parse BeautifulSoup object

        Example:
            class getinfo(CreditInfo):
                def __init__(self, params):
                    super(getinfo, self).__init__()
                    self.params = params

                def otherFunction(self):
                    self._data[table_name].append(value)
                    
            a = getinfo(params)
            a.otherFunction()
            
            return self._data
    """


    def __init__(self):
        """Warning：

            初始化属性不能随意更改，若更改了，则需要更改用到的爬虫脚本里的属性。
        """

        self.qyxx_basicinfo = []
        self.qyxx_s_h = []
        self.qyxx_b_c = []
        self.qyxx_member = []
        self.qyxx_branch = []
        self.qyxx_mortgage_basic = []
        self.qyxx_pledge = []
        self.qyxx_adm_punishment = []
        self.qyxx_abnormal = []
        self.qyxx_black_info = []
        self.qyxx_spot_check = []
        self.qyxx_stock_freeze = []
        self.qyxx_stockholder_change = []
        self.qyxx_c_mortgage = []
        self.qyxx_s_creditor = []
        self.qyxx_mortgage = []

    def returnData(self):
        """将所有属性数据汇总到_data字典中

            返回: _data[tableName] = valueList

        :return:
        """

        self._data = {}
        self._data['qyxx_basicinfo'] = self.qyxx_basicinfo
        self._data['qyxx_s_h'] = self.qyxx_s_h
        self._data['qyxx_b_c'] = self.qyxx_b_c
        self._data['qyxx_member'] = self.qyxx_member
        self._data['qyxx_branch'] = self.qyxx_branch
        self._data['qyxx_mortgage_basic'] = self.qyxx_mortgage_basic
        self._data['qyxx_pledge'] = self.qyxx_pledge
        self._data['qyxx_adm_punishment'] = self.qyxx_adm_punishment
        self._data['qyxx_abnormal'] = self.qyxx_abnormal
        self._data['qyxx_black_info'] = self.qyxx_black_info
        self._data['qyxx_spot_check'] = self.qyxx_spot_check
        self._data['qyxx_stock_freeze'] = self.qyxx_stock_freeze
        self._data['qyxx_stockholder_change'] = self.qyxx_stockholder_change
        self._data['qyxx_c_mortgage'] = self.qyxx_c_mortgage
        self._data['qyxx_s_creditor'] = self.qyxx_s_creditor
        self._data['qyxx_mortgage'] = self.qyxx_mortgage

        return self._data

    @classmethod
    def parse(cls, pageSoup, tag=None, attrs=None, key_list=None,
              **kwargs):
        """提取指定标签下的soup对象，便于调用_find_all函数来获取数据。

        :param pageSoup: 页面BeautifulSoup对象
        :param tag: 标签名，对应find_all里面的name参数
        :param attrs: 标签的属性
        :param key_list: 关键字（表头）列表，list or tuple。
        :param kwargs:
        :return: function _find_all()
        """

        if tag or attrs:
            pageSoup = pageSoup.find(name=tag, attrs=attrs)
        else:
            pageSoup = pageSoup

        if pageSoup:
            return cls._find_all(pageSoup, key_list=key_list, **kwargs)
        else:
            return []

    @classmethod
    def _find_all(cls, pageSoup, key_list=None, **kwargs):
        """根据指定标签的BeautifulSoup对象和关键字列表，
        判断数据排版结构并调用对应的函数获取数据

        :param pageSoup: 指定标签的BeautifulSoup对象
        :param key_list: 关键字（表头）列表，list or tuple。
        :param kwargs:
        :return: function basicType() or upDown()
        """


        typ = cls._judge_type(pageSoup=pageSoup)

        if typ:
            return cls.basicType(pageSoup, key_list=key_list, **kwargs)
        else:
            return cls.upDown(pageSoup, key_list=key_list, **kwargs)

    @classmethod
    def getKeyList(cls, pageSoup, key_list=None, **kwargs):
        """获取对应板块的关键字字段

        :param pageSoup: 指定板块的BeautifulSoup对象
        :param key_list: 关键字（表头）列表，list or tuple。
        :param kwargs:
        :return: 关键字（表头）列表，list or tuple。
        """


        typ = cls._judge_type(pageSoup=pageSoup)
        if typ == None: return None
        if typ:
            try:
                th_tags = pageSoup.find_all('th')
                td_tags = pageSoup.find_all('td')
            except:
                raise ValueError('左右结构找th和td时发生异常')

            if key_list:
                if len(key_list) != len(td_tags):
                    raise ValueError('key_list 的长度与内容的长度不一致。')
                else:
                    key_list = key_list  # 顺序
            else:
                key_list = [th_tags[i].text.strip() for i in
                            xrange(len(th_tags))]  # 顺序
        else:
            try:
                tr_tags = pageSoup.find_all('tr')
            except:
                raise ValueError('上下结构找不到tr')
            if key_list:
                key_list = key_list
            else:
                key_list = []
                for each in tr_tags:
                    th_tags = each.find_all('th')
                    td_tags = each.find_all('td')
                    if len(th_tags) >= 3 and len(td_tags) < 1:
                        for th_tag in th_tags:
                            key = th_tag.text.strip()
                            if key not in key_list:
                                key_list.append(key)
                        break
                    else:
                        continue

        return key_list  # None or list

    @classmethod
    def _judge_type(cls, pageSoup, **kwargs):
        """
        如果同一个tr标签既有th又有td，则类基本信息，type是1，否则是0

        :param pageSoup: 指定板块的BeautifulSoup对象
        :param kwargs
        :return: 数据结构排版类型：
            Example：
                如果是基本信息那种左边是关键字，右边是值的，则 typ = 1：
                如果是股东信息那种（包括主要成员），上边是关键字，下边是值的，则 typ = 0.
        """


        rows = pageSoup.find_all('tr')  # 一行内容是一个 tr 标签
        if rows:
            typ = 0  # 上下排列类型，如股东信息
            for row in rows:
                if row.find('th') and row.find('td'):
                    typ = 1  # 左右排列类型，如基本信息
                    break
                else:
                    continue
            return typ
        else:
            return None  # tr都找不到，说明没有这个版块

    @classmethod
    def basicType(cls, pageSoup, key_list=None, **kwargs):
        """获取key-value属于左右排版的指定板块BeautifulSoup对象的数据

        :param pageSoup: 指定板块BeautifulSoup对象
        :param key_list: 关键字（表头）列表，list or tuple。
        :param kwargs:
        :return: _result_list
        """

        _result_list = []
        _result = {}
        try:
            th_tags = pageSoup.find_all('th')
            td_tags = pageSoup.find_all('td')
        except:
            raise ValueError('左右结构找th和td时发生异常')

        if key_list:
            if len(key_list) != len(td_tags):
                raise ValueError('key_list 的长度与内容的长度不一致。')
            else:
                key_list = key_list  # 顺序
        else:
            key_list = [th_tags[i].text.strip() for i in
                        xrange(len(th_tags))]  # 顺序

        for i in xrange(-1, - 1 - len(td_tags), -1):
            key = key_list[i]
            value = td_tags[i].text.strip()
            _result[key] = value  # 逆序填充

        _result_list.append(_result)

        return _result_list

    @classmethod
    def upDown(cls, pageSoup, key_list=None, **kwargs):
        """获取key-value属于左右排版的指定板块BeautifulSoup对象的数据
        在每一个tr里面找th，该tr不含td且th的个数>3, 则视为表头。

        :param pageSoup: 指定板块BeautifulSoup对象
        :param key_list: 关键字（表头）列表，list or tuple。
        :param kwargs:
        :return: _result_list
        """

        _result_list = []
        try:
            tr_tags = pageSoup.find_all('tr')
        except:
            raise ValueError('上下结构找不到tr')

        key_list = cls.getKeyList(pageSoup, key_list=key_list, **kwargs)
        if key_list == None: return []

        for each in tr_tags:
            _result = {}
            td_tags = each.find_all('td')
            if len(td_tags) < 3:
                continue
            elif len(td_tags) > len(key_list):  # 主要成员 member
                index = (len(td_tags) / len(key_list)) * len(key_list)
                i = 0
                while i < index:
                    for j in xrange(len(key_list)):
                        _result[key_list[j]] = td_tags[i].text.strip()
                        i += 1
                    _result_list.append(_result)
                    _result = {}
                continue
            elif len(td_tags) == len(key_list):  # 大部分应该是这样(更多， 超链接)
                for i, key in enumerate(key_list):
                    if td_tags[i].find('a'):
                        _result = cls._special(key_list, td_tags,
                                                **kwargs)
                        break
                    else:
                        _result[key] = td_tags[i].text.strip()
            else:  # len(td_tags) < len(key_list)
                _result = cls._super_special(key_list, td_tags, **kwargs)

            _result_list.append(_result)

        return _result_list

    @classmethod
    def _special(cls, key_list, td_tags, **kwargs):
        """对于特殊情况len(td_tags) <= len(key_list)处理的函数，
        包括超链接，更多，详情，查看变更前，详细等等。
        :parameters 至少要包含key_list和td_tags

        :param key_list: 关键字（表头）列表，list or tuple。
        :param td_tags: 出现特殊情况的当前行的所有值的 BeautifulSoup 对象列表
            Example：
                第一条股东信息 最后一个字段出现 详情 的超链接，
                则，当前行所在的标签是tr，通过find_all方法找到td标签，
                所返回的结果就是 td_tags.
        :return: _result should be a dict
        """


        _result = {}

        for i, key in enumerate(key_list):
            # 先判断是否有存在‘更多’和‘收起更多’
            more = re.search('(更多)?(.*?)收起更多',
                             td_tags[i].text.strip(), re.S)
            if more:
                print '发现超链接————更多'
                more = re.search('更多(.*?)收起更多',
                                 td_tags[i].text.strip(), re.S)
                if not more:
                    more = re.search('(.*?)收起更多',
                                 td_tags[i].text.strip(), re.S)
                value = more.group(1).strip()
            else:
                link = td_tags[i].find('a')
                if not link:
                    value = td_tags[i].text.strip()
                else:
                    print '发现超链接————详情 or 变更前、变更后等'
                    try:
                        value = link['onclick']
                    except KeyError:
                        value = link['href']
                    except:
                        raise ValueError('未知的超链接属性'.encode('utf-8'))
                    value = link.text.strip() + '>>>' + value
            _result[key] = value.replace('\n',
                                         '').replace('\r',
                                                           '').replace('\t',
                                                                       '')

        return _result

    @classmethod
    def _super_special(cls,  key_list, td_tags, **kwargs):
        """针对一个‘详细’情况占用了两格的情况，也就是说len(td_tags) < len(key_list)"""

        raise ValueError("你需要写针对性的函数来获取'详细'里的信息".encode('utf-8'))

''' 这是用在每个爬虫脚本中的模板，使用时需要检查key_list是否与网址对应。

class CompanyInfo(CreditInfo):
    """继承信用信息类(模板)

    """

    def __init__(self):
        super(CompanyInfo, self).__init__() # 继承父类的__init__
        self.mortgage_reg_num = None    # 存动产抵押登记编号

    def basicinfo_execute(self, **kwargs):
        pass

    # QYXX_S_H登记信息（股东信息）
    def s_h_execute(self, **kwargs):
        key_list = ['s_h_name', 's_h_type',
                    's_h_id_type', 's_h_id', 'detail']

    # QYXX_B_C登记信息（更变信息）
    def b_c_execute(self, **kwargs):
        key_list = ['reason', 'before_change',
                    'after_change', 'date_to_change']

    # QYXX_MEMBER备案信息（主要人员信息）
    def member_execute(self, **kwargs):
        key_list = ['xuhao', 'person_name', 'p_position']

    # QYXX_BRANCH备案信息（分支机构信息）
    def branch_execute(self, **kwargs):
        key_list = ['xuhao', 'company_num',
                    'company_name', 'authority']

    # QYXX_MORTGAGE_BASIC动产抵押登记基本信息
    def mortgage_basic_execute(self, **kwargs):
        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg',
                    'authority', 'amount', 'status',
                    'gongshiriqi', 'detail']

    # QYXX_PLEDGE股权出质登记信息
    def pledge_execute(self, **kwargs):
        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card',
                    'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'gongshiriqi', 'changes']

    # QYXX_ADM_PUNISHMENT行政处罚
    def adm_punishment_execute(self, **kwargs):
        key_list = ['xuhao', 'pun_number', 'reason', 'fines',
                    'authority', 'pun_date', 'gongshiriqi', 'detail']

    # QYXX_ABNORMAL经营异常信息
    def abnormal_execute(self, **kwargs):
        key_list = ['xuhao', 'reason', 'date_occurred',
                        'reason_out', 'date_out', 'authority']

    # QYXX_BLACK_INFO严重违法信息###
    def black_info_execute(self, **kwargs):
        key_list = ['xuhao', 'reason_in', 'date_in',
                        'reason_out','date_out','authority']

    # QYXX_SPOT_CHECK抽查检验信息###
    def spot_check_execute(self, **kwargs):
        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date',
                        'spot_result']

    # QYXX_STOCK_FREEZE股权冻结信息###
    def stock_freeze_execute(self, **kwargs):
        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number',
                        'status', 'detail']

    # QYXX_STOCKHOLDER_CHANGE股权更变信息###
    def stockholder_change_execute(self, **kwargs):
        key_list = ['xuhao','person','stock','person_get','court','detail']

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, **kwargs):
        pass

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, **kwargs):
        pass

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, **kwargs):
        key_list = ['xuhao', 'mortgage_name', 'belongs',
                    'information', 'mortgage_range']
'''