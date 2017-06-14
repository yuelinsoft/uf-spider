# -*- coding:utf-8 -*-

__author__ = 'lijb'

import time, os
from a1_beijing_query import *

Session = requests.Session()

cookies = get_cookies_ticket()[0]

headers = {
    'Host':'qyxy.baic.gov.cn',
    'Referer':'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!getBjQyList.dhtml',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
}

# 声明结果变量
result = {}

# 统一基本信息的key名称
def judge_keyword(dict_ba, dict_keyword):
    '''
    :dict_ba {'A2':'d','B2':'dd','C1':'dw9'}
    :dict_keyword {'A':['A1','A2','A3','A4'],'B':['B1','B2'],'C':['C1']}
    :return: 统一key后的dict
    '''
    for keyword in dict_keyword.keys():
        for prob_keyword in dict_keyword[keyword]:
            if dict_ba.has_key(prob_keyword):
                dict_ba[keyword] = dict_ba.pop(prob_keyword)

    return dict_ba

# 获取主键
def get_report_id():
    '''
    返回插入数据库所需要的主键id
    :return:
    '''

    return 0

# 返回页面或版块的soup对象
def get_html(url, *para):
    '''
    :url: url
    :para: 如果不传，返回(),所有元素组成元组
    :return: 返回页面的html的soup对象
    '''
    headers_info = {
            'Host':'qyxy.baic.gov.cn',
            'Uper-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36'
        }

    if para != ():
        data = para[0]
        req = None
        t = 0
        while t < 10:
            try:
                req = Session.post(url, timeout=20, headers=headers_info, data=data)
                break
            except:
                t += 1
                print u'网络请求失败，第', t + 1, u'次尝试重连……'
    else:
        req = None
        t = 0
        while t < 10:
            try:
                req = Session.post(url, timeout=20, headers=headers_info)
                break
            except:
                t += 1
                print u'网络请求失败，第', t + 1, u'次尝试重连……'
    if req == None:
        print u'多次尝试网络请求失败，请检查网络，然后重启程序。'
        os._exit(0)
    content = req.text
    # print content
    if len(content)<=150:# 这里可以再完善
        return None
    soup = BeautifulSoup(content, 'lxml')

    return soup

# 获取基本信息
def get_dict(pageSoup, *br_keyword, **d):
    '''
    该函数基本上只对基本信息、动产抵押详情的头两个管用
    :param pageSoup: 首页的soup对象
    :param br_keyword: 版块的关键字
    :param d: soup对象的class值，传递方式如class_='detailsList'
    :return: 以字典形式返回所需信息
    '''

    try:
        info = pageSoup.findAll('table', class_=d["class_"])
        names = data = []
        for i in range(len(br_keyword)):
            for x in info:
                p = x.find(text=br_keyword[i])
                if x.find(text=br_keyword[i]) != None:
                    names = x.find_all('th')
                    data = x.find_all('td')
                    break

        if names == data == []: return {}
    except:
        # print("Error: does not have this part.")
        return {}
    names_list = []
    data_list = []
    for name in names[1:]:
        names_list.append(name.text.strip())
    for d in data:
        data_list.append(d.text.strip().replace('\r\n', ''))
    if len(data_list) == 0:
        return {}
    dict_ba = dict(zip(names_list, data_list))

    return dict_ba

# 获取版块信息
def get_dict_list(pageSoup, key_list, *br_keyword):
    '''

    :param pageSoup: 只含有版块soup对象或含有版块的soup对象（需传递br_keyword参数）
    :param number: key 的个数
    :param br_keyword: id 标签名，若没有，下面的代码部分需改成其他，以获取对应的soup对象
    :return: [{},{},{}]
    '''
    try:
        if br_keyword[0] == "":
            data = pageSoup.find_all('td')
        else:
            info = pageSoup.find(id = br_keyword[0])
            data = info.find_all('td')
    except:
        # print("Error: does not have this part.")
        return []
    data_list = []
    for d in data:
        try:
            span = d.find_all('span')[1]  # 判断是否存在更多的点击项，去第二个span标签，beforeMore*
            data_list.append(span.text.replace(u'收起更多', '').strip().replace('\r\n', ''))
        except:
            data_list.append(d.text.strip().replace('\r\n', ''))
        # print d.text.strip().replace('\r\n', '')
    if len(data_list) == 0:
        return []
    dict_ba_list = []
    number = len(key_list)
    while data_list!=[]:
        dict_ba = dict(zip(key_list,data_list[0:number]))
        dict_ba_list.append(dict_ba)
        data_list = data_list[number:]

    return dict_ba_list

# 变更信息中如果出现详细的情况就调用该函数获取变更前与变更后的内容
def get_changeDetail(url):
    '''
    变更信息中如果出现详细的情况就调用该函数获取变更前与变更后的内容
    :param url: 变更信息中出现的详细的url
    :return: 变更前，变更后，分别是列表转换的字符串
    '''
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    table = soup.find_all('table', {'id': 'tableIdStyle'})
    # 变更前
    trs = table[0].find_all('tr')
    before_change = []
    for each_tr in trs[2:]:
        tds = each_tr.find_all('td')
        name = tds[1].text.strip()
        type = tds[2].text.strip()
        name_type = name + '(' + type + ')'
        before_change.append(name_type)
    before_change = ','.join(before_change)
    # print before_change

    # 变更后
    trs = table[1].find_all('tr')
    after_change = []
    for each_tr in trs[2:]:
        tds = each_tr.find_all('td')
        name = tds[1].text.strip()
        type = tds[2].text.strip()
        name_type = name + '(' + type + ')'
        after_change.append(name_type)
    after_change = ','.join(after_change)
    # print after_change

    return before_change, after_change

# 获取最大页码
def get_pagesCount(soup):
    '''

    :param soup: 版块soup对象
    :return: 返回该版块的最大页码，无则返回0
    '''
    pagescount = soup.find('input', {'id': "pagescount"})

    if pagescount != None:

        count = pagescount['value']
    else:
        count = 0

    return int(count)

# 由于各版块在获取内容时形式上相近，所以封装出来以减少代码的行数
def get_info(url, entId, params, key_list):
    '''
    由于各版块在获取内容时形式上相近，所以封装出来以减少代码的行数
    :param url: 版块url
    :param entId: 企业的id
    :param params: params参数，目的是获取里面的 entId 键值
    :param key_list: 版块的字段list
    :return: 字典列表
    '''

    data = {
        'pageNos': 1,
        'ent_id': entId,
        'pageNo': 1,
        'pageSize': 10,
        'clear': 'true'
    }

    res = Session.post(url, params=params, data=data, headers=headers, cookies=cookies)
    soup = BeautifulSoup(res.text, 'lxml')
    pageNum = get_pagesCount(soup)

    # key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type']
    # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型']

    if pageNum == 0:
        return []
    else:  # 如果是大于1页的，先取第一页，再循环第二页之后
        Info = get_dict_list(soup, key_list, '')
        for i in range(2, pageNum + 1):
            data = {
                'pageNos': i,
                'ent_id': entId,
                'pageNo': 1,
                'pageSize': 10,
                'clear': 'true'
            }
            res = Session.post(url, data=data, headers=headers, cookies=cookies)
            soup = BeautifulSoup(res.text, 'lxml')
            info = get_dict_list(soup, key_list, '')

            Info.extend(info)

    return Info

# ——————————上面五个函数是通用的，只需要更改headers里面的值

# 动产抵押详情
def detailPage(soup, id):
    '''
    该函数获取动产抵押详情页面信息并爬取其中三块内容。
    :param soup: 动产抵押登记信息版块的soup对象
    :return:
    '''
    # 带详情的tr标签
    tr = soup.find_all('tr', {'name': 'dc'})
    a = []
    for each in tr:
        td = each.find_all('td')
        # 找第8个 td 标签下的 a 标签
        a.append(td[7].find('a'))
    onclick = []
    if a != []:
    # 进入if，说明存在动产抵押基本信息
        for each in a:
        # 循环 a 标签，获取 onclick
            try:
                click = each['onclick'].split("'")[1]
            except:
                # 有动产抵押登记信息，但是没有详情页面的链接
                break
            onclick.append(click)
        # 循环结束得到的结果是onclick里面的类似于id 的 有效数字字符串的集合
    if onclick != []:
    # 进入if，说明有详情页面。下面就根据onclick里的数字id字符串获取详情页的具体信息
        url = 'http://qyxy.baic.gov.cn'
        for click in onclick:
            data = {
                'method': 'dcdyDetail',
                'maent.pripid': id,
                'maent.xh': click,
                'random': str(int(time.time() * 1000))
            }
            # 单个动产抵押详情的soup对象，可用该对象实例化pool_d类
            soup = get_html(url, data)
            pool = Pool_d()
            execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
            tableListC = ['dispatcher_qyxx_c_mortgage', 'dispatcher_qyxx_s_creditor', 'dispatcher_qyxx_mortgage']
            for i in range(len(execute_d)):
                print '*' * 20, execute_d[i], '*' * 20
                # print getattr(pool, exe)(soup)
                result[tableListC[i]] = getattr(pool, execute_d[i])(soup)

# 动产抵押详情
class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        br_keyword = u"动产抵押登记信息"
        dict_ba = get_dict(pageSoup, br_keyword, class_="detailsList")

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return dict_ba

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        br_keyword = u"被担保债权概况"
        dict_ba = get_dict(pageSoup, br_keyword, class_='detailsList')

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        return dict_ba

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):
        br_keyword = u"table_dywgk"
        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information', 'mortgage_range']
        # key_list = ['序号', '抵押物名称', '所有权归属', '数量、质量等信息', '备注']
        dict_ba_list = get_dict_list(pageSoup, key_list, br_keyword)

        mortgageInfo = []
        for dict_ba in dict_ba_list:
            mortgage_reg_num = self.c_mortgage_execute(pageSoup)[u'登记编号']
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
            mortgageInfo.append(dict_ba)

        return dict_ba_list  # 抵押物概况

# ————————————————————上面几个函数是专用于动产抵押情况的

# 工商公示信息类
class Pool():
    '''
    工商公示信息类
    '''
    def __init__(self):

        pass

    # 登记信息部分
    def basicinfo_execute(self, params):
        '''
        :return: 基本信息 dict
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!openEntInfo.dhtml'
        response = Session.get(url, headers=headers, params=params, cookies=cookies)
        soup = BeautifulSoup(response.text, 'lxml')
        soup = soup.find('div', {'id': 'jbxx'})
        br_keyword = u'基本信息 '
        br_keyword_1 = u'基本信息'
        Info = get_dict(soup, br_keyword, br_keyword_1, class_='detailsList')

        dict_keyword = dict(reg_num=[u'注册号', u'注册号/统一社会信用代码'], company_name=[u'名称', u'公司名称'],
                            owner=[u'法定代表人', u'负责人', u'股东', u'经营者', u'执行事务合伙人', u'投资人'],
                            address=[u'营业场所', u'经营场所', u'住所', u'住所/经营场所'], start_date=[u'成立日期', u'注册日期'],
                            check_date=[u'核准日期', u'发照日期'], fund_cap=[u'注册资本'],
                            company_type=[u'类型'], business_area=[u'经营范围'], business_from=[u'经营期限自', u'营业期限自'],
                            check_type=[u'登记状态', u'经营状态'],
                            authority=[u'登记机关'], locate=[u'区域'])

        Info[u'区域'] = u'北京市'
        Info = judge_keyword(Info, dict_keyword)

        Info_list = []
        Info_list.append(Info)

        return Info_list

    # 股东信息
    def s_h_execute(self, params):
        '''

        :param params: 包含企业id的query文件中返回的params
        :return:
        '''

        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!tzrFrame.dhtml'
        key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type']
        # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型']
        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        return Info

    # 变更信息
    def b_c_execute(self, params):
        '''
        :return: 变更信息
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!biangengFrame.dhtml'
        ent_id = params['entId']
        data = {
            'pageNos': 1,
            'ent_id': ent_id,
            'pageNo': 1,
            'pageSize': 5,
            'clear': 'true'
        }
        res = Session.post(url, data=data, headers=headers, cookies=cookies)
        soup = BeautifulSoup(res.text, 'lxml')
        pageNum = get_pagesCount(soup)
        key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
        # key_list = ['变更事项', '变更前', '变更后', '变更日期']
        if pageNum == 0:
            return []
        else:
            Info = []
            for i in range(1, pageNum + 1):
                data = {
                    'pageNos': i,
                    'ent_id': ent_id,
                    'pageNo': 1,
                    'pageSize': 5,
                    'clear': 'true'
                }
                res = Session.post(url, data=data, headers=headers, cookies=cookies)
                soup = BeautifulSoup(res.text, 'lxml')
                # 找到每一页的soup对象
                tr = soup.find_all('tr')    # 先找该对象（版块）下的tr标签，一个tr标签是一行内容
                for each_tr in tr:
                    td = each_tr.find_all('td')     # 再迭代每一个tr标签，寻找td标签，一个td标签是一格内容
                    if td == []:
                        # print u'无td标签'
                        continue
                    elif len(td) == 4:
                        data_list = []
                        for each_td in td:
                            data_list.append(each_td.text)
                        dict_ba = dict(zip(key_list, data_list))

                    else:   # 如果td标签只有三个，说明变更信息存在详细内容
                        data_list = []

                        data_list.append(td[0].text)
                        detail_url = 'http://qyxy.baic.gov.cn' + td[1].a['onclick'].split("'")[1]  # 第二个td标签为详细，
                        qian, hou = get_changeDetail(detail_url)                                   # 通过调用get_changeDetail函数获取变更前与变更后的内容，返回两个字符串
                        data_list.append(qian)
                        data_list.append(hou)
                        data_list.append(td[2].text)
                        dict_ba = dict(zip(key_list, data_list))

                    Info.append(dict_ba)

        return Info

    # 备案信息——主要成员信息
    def member_execute(self, params):
        '''
        :return: 主要成员信息 list, 是 [姓名，职位] 列表
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!zyryFrame.dhtml'

        key_list = ['xuhao', 'person_name', 'p_position']
        # key_list = ['序号', '姓名', '职位']

        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        return Info

    # 备案信息——分支机构信息
    def branch_execute(self, params):
        '''
        :return: 分支机构信息
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!fzjgFrame.dhtml'

        key_list = ['xuhao', 'company_num', 'company_name', 'authority']
        # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        return Info

    # 动产抵押登记
    def mortgage_basic_execute(self, params):
        '''
        :return: 动产抵押登记信息
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbjTab/gjjTabQueryCreditAction!dcdyFrame.dhtml'

        key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority', 'amount', 'status', 'detail']
        # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'详情']
        params = {
            'entId': params['entId'],
            'clear': 'true'
        }
        entId = params['entId']
        Info = get_info(url, entId, params, key_list)

        if Info != []:
            raise ValueError("dict_ba_list is not empty.")

        return Info

    # 股权出资登记信息
    def pledge_execute(self, params):
        '''
        :return: 股权出资登记信息
        '''
        url = 'http://qyxy.baic.gov.cn/gdczdj/gdczdjAction!gdczdjFrame.dhtml'

        key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount', 'brower', 'brower_id_card',
                    'reg_date', 'status', 'changes']
        # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
        # '股权出质设立登记日期', '状态', '变化情况']
        params = {
            'entId': params['entId'],
            'clear': 'true'
        }
        entId = params['entId']
        Info = get_info(url, entId, params, key_list)

        if Info != []:
            raise ValueError("dict_ba_list is not empty.")

        return Info

    # 行政处罚信息
    def adm_punishment_execute(self, params):
        '''
        :return: 行政处罚信息
        '''
        url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list.dhtml'

        key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority', 'pun_date', 'xiangqing']
        # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
        #             '作出行政处罚决定日期','详情']
        params = {
            'entId': params['entId'],
            'clear': 'true'
        }
        entId = params['entId']
        Info = get_info(url, entId, params, key_list)

        if Info != []:
            raise ValueError("dict_ba_list is not empty.")

        return Info

    # 经营异常信息
    def abnormal_execute(self, params):
        '''
        :return: 经营异常信息
        '''
        url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_jyycxx.dhtml'

        key_list = ['xuhao', 'reason', 'date_occurred', 'juedinglierujiguan', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号', '列入异常原因', '列入日期', '作出决定机关（列入）', '移出异常原因', '移出日期', '作出决定机关（列出）']

        params = {
            'entId': params['entId'],
            'clear': 'true'
        }
        entId = params['entId']
        Info = get_info(url, entId, params, key_list)

        # if Info != []:
        #     raise ValueError("dict_ba_list is not empty.")

        return Info

    # 严重违法信息
    def black_info_execute(self, params):
        '''
        :return: 严重违法信息
        '''
        url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_yzwfxx.dhtml'

        key_list = ['xuhao', 'reason_in', 'date_in', 'reason_out', 'date_out', 'authority']
        # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']

        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        if Info != []:
            raise ValueError("dict_ba_list is not empty.")

        return Info

    # 抽查检查信息
    def spot_check_execute(self, params):
        '''
        :return: 抽查检查信息
        '''
        url = 'http://qyxy.baic.gov.cn/gsgs/gsxzcfAction!list_ccjcxx.dhtml'

        key_list = ['xuhao', 'authority', 'spot_type', 'spot_date', 'spot_result']
        # key_list = ['序号','检查实施机关','类型','日期','结果']

        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        # if Info != []:
        #     raise ValueError("dict_ba_list is not empty.")

        return Info

    # 股权冻结信息
    def stock_freeze_execute(self, params):
        '''
        :return:
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!tzrFrame.dhtml'

        key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number', 'status', 'xiangqing']
        # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']

        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        if Info != []:
            raise ValueError("dict_ba_list is not empty.")

        return Info

    # 股东变更信息
    def stockholder_change_execute(self, params):
        '''
        :return: 司法股东变更登记信息 or 行政处罚信息
        '''
        url = 'http://qyxy.baic.gov.cn/gjjbj/gjjQueryCreditAction!tzrFrame.dhtml'

        key_list = ['xuhao', 'person', 'stock', 'person_get', 'court', 'xiangqing']
        # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']

        params = {
            'ent_id': params['entId'],
            'clear': 'true'
        }
        entId = params['ent_id']
        Info = get_info(url, entId, params, key_list)

        if Info != []:
            raise ValueError("dict_ba_list is not empty.")

        return Info

def main(params):
    # 实例化
    pool = Pool()

    # 工商公示
    executeA = ['mortgage_basic_execute', 'pledge_execute', 'adm_punishment_execute',
                'black_info_execute', 'spot_check_execute',
                'basicinfo_execute', 's_h_execute', 'b_c_execute',
                'member_execute', 'branch_execute','abnormal_execute']

    tableListA = ['dispatcher_qyxx_mortgage_basic', 'dispatcher_qyxx_pledge',
                  'dispatcher_qyxx_adm_punishment', 'dispatcher_qyxx_black_info', 'dispatcher_qyxx_spot_check',
                  'dispatcher_qyxx_basicinfo', 'dispatcher_qyxx_s_h', 'dispatcher_qyxx_b_c',
                  'dispatcher_qyxx_member', 'dispatcher_qyxx_branch',
                  'dispatcher_qyxx_abnormal']

    print "-" * 20, u'工商公示信息', "-" * 20
    for i in range(len(executeA)):
        print "-" * 20, executeA[i], "-" * 20
        # print getattr(pool, each_get)(params)
        # print pool.basicinfo_execute(params)
        result[tableListA[i]] = getattr(pool, executeA[i])(params)

    # 目前没发现动产抵押与司法协助

    print 'Finished……'

if __name__ == '__main__':
    params = mainP(u'北京紫晶立方科技有限公司')
    # params = [{
    #     'entId': '20e38b8b445ec474014477501174544c',
    #     'credit_ticket': 'A89CA33CBAF5BB13F2C0E5E9069C338C', # 这个值会变的
    #     'entNo': '110108016798112',
    #     # 'clear': 'true'
    #     # 'timeStamp': str(int(time.time() * 1000))
    # }]
    main(params[0])
