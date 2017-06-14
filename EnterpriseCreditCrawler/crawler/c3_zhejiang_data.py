# -*- coding:utf-8 -*-

from bs4 import BeautifulSoup
from c3_zhejiang_query import *

Session = requests.Session()

# 返回页面或版块的soup对象
def get_html(url, *para):
    '''
    :url: url
    :para: 如果不传，返回(),所有元素组成元组
    :return: 返回页面的html的soup对象
    '''
    headers_info = {
            'Host':'gsxt.zjaic.gov.cn',
            # 'Referer': 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + '20C5BB729DBC540C6220EB5F9F21DF819BD7E287A4D4949E813A02B06D856C6D',
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
def get_Info(soup, key_list=None):
        '''
        :param soup: 具体版块的soup 对象，该soup对象只能包含一个版块或模块信息，不能是包含很多个版块的soup对象
        :keys_count: 由于无法根据th的个数来确定keys标签的个数，因此作为参数进行传递
        :return: 包含字典的列表 类似 [{},{}]
        '''
        # 需要爬取的keys
        Info = []
        if soup != None:
            th = soup.find_all('th')
            td = soup.find_all('td')
            if len(td) == 0:
                return []

            keys = []  # 用来存有序key
            if key_list == None:
                th = th[1:]
                for each in th:
                    key = each.text.strip()
                    if key not in keys:
                        keys.append(key)
            else:
                keys = key_list
            #     th = th[1: int(len(key_list)) + 1]
            # for each in th:
            #     key = each.text.strip()
            #     if key not in keys:
            #         keys.append(key)

            values = []  # 用来存有序value
            for each in td:
                value = each.text.strip().replace('\r\n', '').replace(' ', '')
                values.append(value)

            if len(values) >= len(keys):
                Info = []
                j = 0  # values 的下标
                t = 0  # 记录items的条数
                while t < len(values) / len(keys):
                    i = 0  # keys 的下标
                    info = {}
                    while i < len(keys):
                        info[keys[i]] = values[j]
                        i += 1
                        j += 1
                    Info.append(info)
                    t += 1
            else:
                Info = []

        return Info

# 获取版块信息
# def get_dict_list(pageSoup, number, *br_keyword):
#     '''
#
#     :param pageSoup: 只含有版块soup对象或含有版块的soup对象（需传递br_keyword参数）
#     :param number: key 的个数
#     :param br_keyword: id 标签名，若没有，下面的代码部分需改成其他，以获取对应的soup对象
#     :return: [{},{},{}]
#     '''
#     try:
#         if br_keyword[0] == "":
#             data = pageSoup.find_all('td')
#         else:
#             info = pageSoup.find(id = br_keyword[0])
#             data = info.find_all('td')
#     except:
#         # print("Error: does not have this part.")
#         return []
#     data_list = []
#     for d in data:
#         data_list.append(d.text.strip().replace('\r\n', ''))
#         # print d.text.strip().replace('\r\n', '')
#     if len(data_list) == 0:
#         return []
#     dict_ba_list = []
#     while data_list!=[]:
#         dict_ba = dict(zip([str(i) for i in range(number)],data_list[0:number]))
#         dict_ba_list.append(dict_ba)
#         data_list = data_list[number:]
#
#     return dict_ba_list

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

# ——————————上面五个函数是通用的，只需要更改headers里面的值

# 动产抵押详情
def detailPage(soup, id):
    '''
    该函数获取动产抵押详情页面信息并爬取其中三块内容。
    :param soup: 动产抵押登记信息版块的soup对象
    :return:
    '''
    # 找到动产抵押的div标签
    # div = soup.find('div',{'id': 'dongchandiya'})
    # 找到所有的td标签
    td = soup.find_all('td')
    # 存放所有详情页的url
    urls = []
    # 迭代所有td标签，找到带详情的a标签
    for each in td:
        a = each.find('a')
        if a != None:
            # 拼出详情页的url
            url = 'http://gsxt.zjaic.gov.cn' + a['href']
            urls.append(url)


    if urls != []:
    # 进入if，说明存在动产抵押基本信息
        for each in urls:
        # 循环 迭代所有详情url

            headers = {
                    'Host': 'gsxt.zjaic.gov.cn',
                    'Referer': 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + id,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
                }

            # 单个动产抵押详情的soup对象，可用该对象实例化pool_d类
            data = {
                'dcdyPawnPagination.currentPage': 1,
                'dcdyPawnPagination.pageSize': 100  # 设置一个尽可能大的页数，以便于一次性返回所有抵押物详情的数据
            }
            html = Session.post(each, data=data, headers=headers).text
            soup = BeautifulSoup(html, 'lxml')
            pool = Pool_d()
            execute_d = ['c_mortgage_execute', 's_creditor_execute', 'mortgage_execute']
            for exe in execute_d:
                print '*' * 20, exe, '*' * 20
                print getattr(pool, exe)(soup)

# 动产抵押详情
class Pool_d():

    def __init__(self):
        pass

    # QYXX_C_MORTGAGE动产抵押登记信息（动产抵押登记信息）
    def c_mortgage_execute(self, pageSoup):
        br_keyword = u"动产抵押登记信息"
        dict_ba = get_dict(pageSoup, br_keyword, class_="detailsList")

        dict_keyword = dict(mortgage_reg_num=[u'登记编号'], date_reg=[u'登记日期'], authority=[u'登记机关'],
                            mortgage_type=[u'被担保债权种类'], amount=[u'被担保债权数额'],
                            time_range=[u'债务人履行债务的期限'], mortgage_range=[u'担保范围'])
        dict_ba = judge_keyword(dict_ba, dict_keyword)

        Info_list = []
        Info_list.append(dict_ba)

        return Info_list

    # QYXX_S_CREDITOR动产抵押登记信息（被担保债权概况）
    def s_creditor_execute(self, pageSoup):
        br_keyword = u"被担保债权概况"
        dict_ba = get_dict(pageSoup, br_keyword, class_='detailsList')

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0][u'mortgage_reg_num']
        dict_ba['mortgage_reg_num'] = mortgage_reg_num

        dict_keyword = dict(mortgage_type=[u'种类'], amount=[u'数额'],
                            time_range=[u'债务人履行债务的期限'], mortgage_range=[u'担保的范围'])
        dict_ba = judge_keyword(dict_ba, dict_keyword)

        Info_list = []
        Info_list.append(dict_ba)

        return Info_list

    # QYXX_MORTGAGE动产抵押登记信息（抵押物概况）
    def mortgage_execute(self, pageSoup):

        table = pageSoup.find('div', {'id': 'qufenkuang'})
        table = table.find_all('table')[3]
        # 调用下面的get_Info函数
        key_list = ['xuhao', 'mortgage_name', 'belongs', 'information', 'mortgage_range']
        # value_list = [u'序号', u'抵押物名称', u'所有权归属', u'数量', u'质量等信息', u'备注']
        Info = get_Info(table, key_list)

        mortgage_reg_num = self.c_mortgage_execute(pageSoup)[0][u'mortgage_reg_num']

        mortgageInfo = []
        for dict_ba in Info:
            dict_ba['mortgage_reg_num'] = mortgage_reg_num
            mortgageInfo.append(dict_ba)

        return mortgageInfo

# ————————————————————上面几个函数是专用于动产抵押情况的

# 工商公示信息类（包含司法协助）
class Pool():

    def __init__(self, id):
        '''
        :param id: id
        '''
        self.id = id
        self.headers = {
                    'Host': 'gsxt.zjaic.gov.cn',
                    'Referer': 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id,
                    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
                }

    # 基本信息
    def basicinfo_execute(self):
        # 拿首页的soup
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url,headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_1'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            # br_keyword = u'基本信息'
            soup = soup.find('table', {'class': 'detailsList'})
            # jiben = get_Info(soup)
            Info = get_Info(soup)[0]
            dict_keyword = dict(REG_NUM=[u'注册号', u'注册号/统一社会信用代码'], COMPANY_NAME=[u'名称', u'公司名称'],
                                OWNER=[u'法定代表人', u'负责人', u'股东', u'经营者', u'执行事务合伙人', u'投资人'],
                                ADDRESS=[u'营业场所', u'经营场所', u'住所', u'住所/经营场所'], START_DATE=[u'成立日期', u'注册日期'],
                                CHECK_DATE=[u'核准日期', u'发照日期'], FUND_CAP=[u'注册资本'],
                                COMPANY_TYPE=[u'类型'], BUSINESS_AREA=[u'经营范围'], BUSINESS_FROM=[u'经营期限自'],
                                CHECK_TYPE=[u'登记状态', u'经营状态'],
                                AUTHORITY=[u'登记机关'], LOCATE=[u'区域'])
            Info[u'区域'] = u'浙江省'
            Info = judge_keyword(Info, dict_keyword)

            return Info

        # 股东信息

    # 股东信息
    def s_h_execute(self):
        '''
        :return: 股东信息
        '''
        # 拿首页的soup
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_1'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            # 遇到翻页的版块，只需要在下面添加一个data参数，并post请求传递，即可返回该版块所有信息。
            data = {
                'entInvestorPagination.currentPage': 1,
                'entInvestorPagination.pageSize': 100   # 设置一个尽可能大的参数，以便一次性返回所有股东信息
            }
            html = Session.post(url, data=data, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            # 判断是否有股东信息
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[1]
                if u'投资人' in soup.find('th', {'style': 'text-align: center;'}).text:
                    key_list = [u'姓名', u'出资方式']
                    Info = get_Info(soup, key_list)
                else:
                    key_list = ['s_h_name', 's_h_id_type', 's_h_id', 's_h_type', 'detail']
                    # key_list = ['股东', '股东证件类型', '股东证件号', '股东类型', '详情']
                    Info = get_Info(soup, key_list)

                return Info
            except:
                return []

    # 变更信息
    def b_c_execute(self):
        '''
        :return: 变更信息
        '''
        # 拿首页的soup
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_1'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            data = {
                'checkAlterPagination.currentPage':1,
                'checkAlterPagination.pageSize':100
            }
            html = Session.post(url, data=data, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            # 判断是否有变更信息
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[-1]
                if u'变更' in soup.find('th', {'style': 'text-align: center;'}).text:
                    key_list = ['reason', 'before_change', 'after_change', 'date_to_change']
                    # key_list = ['变更事项', '变更前', '变更后', '变更日期']
                    Info = get_Info(soup, key_list)

                    return Info
                else:
                    return []
            except:
                return []

    # 备案信息——主要成员信息
    def member_execute(self):
        '''
        :return: 主要成员信息 list, 是 [姓名，职位] 列表
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_3'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                if u'主要人员' in soup.find('th', {'style': 'text-align:center;'}).text:
                    key_list = ['xuhao', 'person_name', 'p_position']
                    # key_list = ['序号', '姓名', '职位']
                    Info = get_Info(soup, key_list)

                    return Info
                else:
                    return []
            except:
                return []

    # 备案信息——分支机构信息
    def branch_execute(self):
        '''
        :return: 分支机构信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_3'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            # 判断是否有分支机构信息
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[1]
                if u'分支机构' in soup.find('th', {'style': 'text-align:center;'}).text:
                    key_list = ['xuhao', 'company_num', 'company_name', 'authority']
                    # key_list = ['序号', '注册号/统一社会信用代码', '名称', '登记机关']
                    Info = get_Info(soup, key_list)   # 调用面的get_Info函数

                    return Info
                else:
                    return []
            except:
                return []

    # 动产抵押登记
    def mortgage_basic_execute(self):
        '''
        :return: 动产抵押登记信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_5'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'mortgage_reg_num', 'date_reg', 'authority', 'amount', 'status', 'detail']
                # key_list = ['序号'	'登记编号'	'登记日期'	'登记机关'	'被担保债权数额'	'状态'	'详情']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数

                return Info
            except:
                return []

    # 股权出资登记信息
    def pledge_execute(self):
        '''
        :return: 股权出资登记信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_4'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']

            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'reg_code', 'pleder', 'id_card', 'plede_amount', 'brower', 'brower_id_card',
                            'reg_date', 'status', 'changes']
                # key_list = ['序号', '登记编号', '出质人', '证件号码', '出质股权数额', '质权人', '证件号码',
                # '股权出质设立登记日期', '状态', '变化情况']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数
                if Info != []:
                    raise ValueError("dict_ba_list is not empty.")

                return Info
            except:
                return []

    # 行政处罚信息
    def adm_punishment_execute(self):
        '''
        :return: 行政处罚信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_6'})
        Info = []
        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'pun_number', 'reason', 'fines', 'authority', 'pun_date', 'detail']
                # key_list = ['序号','行政处罚决定书文号','违法行为类型','行政处罚内容','作出行政处罚决定机关名称',
                #             '作出行政处罚决定日期','详情']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数
                if Info != []:
                    raise ValueError("dict_ba_list is not empty.")

                return Info
            except:
                return []

    # 经营异常信息
    def abnormal_execute(self):
        '''
        :return: 经营异常信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_7'})
        Info = []
        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'reason', 'date_occurred', 'reason_out', 'date_out', 'authority']
                # key_list = ['序号', '列入异常原因', '列入日期', '移出异常原因', '移出日期', '作出决定机关']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数

                return Info
            except:
                return []

    # 严重违法信息
    def black_info_execute(self):
        '''
        :return: 严重违法信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_8'})
        Info = []
        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'reason_in', 'date_in', 'reason_out', 'date_out', 'authority']
                # key_list = ['序号','列入严重违法失信企业名单原因','列入日期','移出严重违法失信企业名单原因','移出日期','作出决定机关']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数
                if Info != []:
                    raise ValueError("dict_ba_list is not empty.")

                return Info
            except:
                return []

    # 抽查检查信息
    def spot_check_execute(self):
        '''
        :return: 抽查检查信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_9'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'authority', 'spot_type', 'spot_date', 'spot_result']
                # key_list = ['序号','检查实施机关','类型','日期','结果']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数

                return Info
            except:
                return []

    # 股权冻结信息
    def stock_freeze_execute(self):
        '''
        :return: 股权冻结信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/jsp/client/biz/view/justiceInfoPublic.jsp?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_1'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'person', 'stock', 'court', 'notice_number', 'status', 'detail']
                # key_list = ['序号',	'被执行人',	'股权数额',	'执行法院',	'协助公示通知书文号',	'状态',	'详情']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数
                if Info != []:
                    raise ValueError("dict_ba_list is not empty.")

                return Info
            except:
                return []

    # 股东变更登记信息
    def stockholder_change_execute(self):
        '''
        :return: 股东变更登记信息
        '''
        url = 'http://gsxt.zjaic.gov.cn/jsp/client/biz/view/justiceInfoPublic.jsp?corpid=' + self.id
        html = Session.get(url, headers=self.headers).text
        soup = BeautifulSoup(html, 'lxml')
        # 拿分页soup
        url = soup.find('iframe', {'id': 'con_nav_ifm_2'})

        if url != None:
            # 拼接版块url
            url = 'http://gsxt.zjaic.gov.cn' + url['url']
            html = Session.get(url, headers=self.headers).text
            soup = BeautifulSoup(html, 'lxml')
            # print soup.prettify()
            try:
                soup = soup.find_all('table', {'class': 'detailsList'})[0]
                key_list = ['xuhao', 'person', 'stock', 'person_get', 'court', 'detail']
                # key_list = ['序号','被执行人','股权数额','受让人','执行法院','详情']
                Info = get_Info(soup, key_list)  # 调用面的get_Info函数
                if Info != []:
                    raise ValueError("dict_ba_list is not empty.")

                return Info
            except:
                return []

def main(name):

    # 获取corpid
    id = get_Id(name)

    pool = Pool(id)

    # 工商公示
    executeA = ['black_info_execute','pledge_execute', 'adm_punishment_execute',
                'stock_freeze_execute', 'stockholder_change_execute',
                'basicinfo_execute', 's_h_execute', 'b_c_execute',
                'member_execute', 'branch_execute',
                'mortgage_basic_execute', 'abnormal_execute','spot_check_execute']

    print "-" * 20, u'工商公示信息', "-" * 20
    for each_get in executeA:
        print "-" * 20, each_get, "-" * 20
        print getattr(pool, each_get)()
        # print pool.member_execute()
# —————————————————动产抵押详情——————————————————————————————————————————————————————————————————————————
    headers = {
        'Host': 'gsxt.zjaic.gov.cn',
        'Referer': 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + id,
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36'
    }
    url = 'http://gsxt.zjaic.gov.cn/appbasicinfo/doViewAppBasicInfo.do?corpid=' + id
    html = Session.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    # 拿分页soup
    url = soup.find('iframe', {'id': 'con_nav_ifm_5'})

    if url != None:
        # 拼接版块url
        url = 'http://gsxt.zjaic.gov.cn' + url['url']
        html = Session.get(url, headers=headers).text
        soup = BeautifulSoup(html, 'lxml')
        try:
            soup = soup.find_all('table', {'class': 'detailsList'})[0]
            # 如果把detailPage函数的调用放到Pool类的动产抵押登记信息里，上面一段代码可以省略
            detailPage(soup, id)
        except:
            return []
# ————————————————————————————————————————————————————————————————————————————————————————————————————————

    print 'Finished……'

if __name__ == '__main__':

    name = [u'杭州博创幕墙有限公司',
            u'金华市华超金属回收有限公司西埠头收购部',
            u'海盐溢利自攻螺钉厂',  # 动产抵押
            u'宁波市青华漆业有限公司', # 变更信息有翻页
            u'乐清市乐成林双油漆店', # 变更信息翻页
            u'宁波中洲华海投资有限公司',
            u'宁波杉鹏投资有限公司',
            u'宁波磐鑫投资管理中心（有限合伙）',
            u'宁波天晟达投资有限公司',
            u'浙江海派资产管理有限公司'] # 股东信息有翻页

    for i in range(9,10):
        main(name[2])


