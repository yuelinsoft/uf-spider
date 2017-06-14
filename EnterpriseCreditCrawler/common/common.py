# -*- coding: utf-8 -*-
# author: 'KEXH'

from __future__ import unicode_literals
import re
import json
from bs4 import BeautifulSoup

#### 数据规整与打印 ####

def for_print(result):
    if result == None:
        print None
    elif isinstance(result, list):
        for d in result:
            for key in d:
                print key, d[key]
    else:
        for key in result:
            print key, result[key]

def refine_date(reS):
    # 日期可能开头末尾包含小括号，中括号，中间有/.-和汉字等。
    reP = "19|20\d{2}\D{1,3}\d{1,2}\D{1,3}\d{1,2}"
    pattern1 = re.findall(reP, reS)
    if pattern1 == []:
        return ""
    else:
        p0 = pattern1[0]
        J = ""
        for j in p0:
            if j.isdigit():
                J=J+str(j)
            else:
                J=J+" "
        p1=J.split()
        p2= str(p1[0] + "-" + p1[1] + "-" + p1[2])
        return p2

def judge_keyword(dict_ba, dict_keyword):
    '''
    dict_ba = {'A2':'dddd','B2':'ddafoas','C1':'dkjsajle9w9'}
    dict_keyword = {'A':['A1','A2','A3','A4'],'B':['B1','B2'],'C':['C1'],}
    [return]
    dict_ba = {'A':'dddd','B':'ddafoas','C':'dkjsajle9w9'}
    '''
    for keyword in dict_keyword:
        for prob_keyword in dict_keyword[keyword]:
            if dict_ba.has_key(prob_keyword):
                dict_ba[keyword] = dict_ba.pop(prob_keyword)

    return dict_ba

def judge_province(company_city, prov_dict):
    """

    :param wordList: (company_address, company)
    :param prov_dict: 配置文件里的
    :return:

    Example：
        wordList = ('广东省广州市xx街xx号', '广州市挣他一个亿有限公司')
        prov_dict = {
            '北京':'a1_beijing',
            '天津':'a2_tianjin',
            '内蒙古':'a5_neimenggu'
            }
        [return]
        keyword = 'a5_neimenggu'
    """

    province = None

    for keyword in prov_dict.keys():
        if keyword in company_city:  # 判断地址
            province = keyword
            break
        else:
            continue

    return province

def judge_keyword_1(dict_ba_list, dict_keyword):
    '''
    dict_ba_list = [{'A2':'dddd','B2':'ddafoas','C1':'dkjsajle9w9'},{'A2':'2dddd','B1':'112ddafoas','C1':'222dkjsajle9w9'}]
    dict_keyword = {'A':['A1','A2','A3','A4'],'B':['B1','B2'],'C':['C1']}
    [return]
    dict_ba_list = [{'A': 'dddd', 'C': 'dkjsajle9w9', 'B': 'ddafoas'}, {'A': '2dddd', 'C': '222dkjsajle9w9', 'B': '112ddafoas'}]
    '''
    for keyword in dict_keyword:
        for prob_keyword in dict_keyword[keyword]:
            for dict_ba in dict_ba_list:
                if dict_ba.has_key(prob_keyword):
                    dict_ba[keyword] = dict_ba.pop(prob_keyword)
    return dict_ba_list

def basicinfo_dict(dict_ba,province_name):
    dict_keyword = {
                'company_name':[u'名称',u'企业名称',u'公司名',u'公司名称',u'分支机构名称',u'企业中文名称',u'机构名称'],
                'fund_cap':[u'注册资本'],
                'company_type':[u'类型',u'企业类型',u'组成形式'],
                'check_type':[u'登记状态'],
                'authority':[u'登记机关'],
                'check_date':[u'核审日期', '核准日期'],
                'locate':[u'区域'],
                'owner': [u'法定代表人',u'负责人',u'股东',u'经营者',u'执行事务合伙人',u'投资人',u'执行合伙人',u'首席代表'],
                'address': [u'住所',u'营业场所',u'经营场所',u'住所/经营场所'],
                'reg_num': ['统一社会信用代码', u'注册号',u'注册号/统一社会信用代码','统一社会信用代码/注册号'],
                'business_area': [u'经营范围',u'业务范围'],
                'start_date': [u'成立日期',u'注册日期'],
                'business_from': [u'营业期限自',u'经营期限自'],
                # 下面这几个是深圳才要用到的
                '': [u'认缴注册资本总额',u'注册资金'],
                '': [u'警示信息'],
                '': [u'企业登记状态'],
                '': [u'纳税人状态'],

    }
    dict_ba['区域'] = province_name
    dict_ba = judge_keyword(dict_ba, dict_keyword)
    return dict_ba

def c_mortgage_dict(dict_ba):
    dict_keyword = {
                    'mortgage_reg_num': [u'登记编号'],
                    'date_reg': [u'登记日期'],
                    'authority': [u'登记机关'],
                    'mortgage_type': [u'被担保债权种类'],
                    'amount': [u'被担保债权数额'],
                    'time_range': [u'债务人履行债务的期限'],
                    'mortgage_range': [u'担保范围']
                }
    dict_ba = judge_keyword(dict_ba, dict_keyword)
    return dict_ba

def s_creditor_dict(dict_ba):
    dict_keyword = {
                'mortgage_type': [u'种类'],
                'amount': [u'数额'],
                'mortgage_range': [u'担保的范围'],
                'time_range': [u'债务人履行债务的期限']
            }
    dict_ba = judge_keyword(dict_ba, dict_keyword)
    return dict_ba

#### 数据解析 ####

def parse_url(listPage, *lp_keyword):
    '''
    【如何传值进来】
    lp_keyword, a tuple. 只有两个值的时候直接soup.findAll，如果有四个值，那么后两个值是用于判断页面内容本身是否符合需求的。
    【返回值的使用】
    if result_list == None:
        return main(name)
    else:
        return result_list
    '''
    # 目前用到的省份：广西，安徽，上海，河北，云南，青海，湖南，湖北，河南
    result_list = []
    soup = BeautifulSoup(listPage, 'lxml')
    if len(lp_keyword)<=2 or (len(lp_keyword)>=4 and soup.find (lp_keyword[2], style=lp_keyword[3]) is None):
        try:
            data_list = soup.findAll(lp_keyword[0], class_=lp_keyword[1])
        except:
            data_list = []
        for data in data_list:
            result_list.append(data.a['href'])
    else:
        result_list = None
    return result_list

def get_dict(pageSoup, *br_keyword, **d):
    # **d: get info
    # *br_keyword: get names and data, a tuple like this : ([]).
    # 目前用到的省份：河北，上海，安徽，青海，云南，湖南，湖北，河南，广西，辽宁，吉林，山东。
    try:
        info = pageSoup.findAll('table', class_= d["class_"])
        names=data=[]
        for i in range(len(br_keyword)):
            if [x for x in info if x.find(text=br_keyword[i]) != None] != []:
                a = [x for x in info if x.find(text=br_keyword[i]) != None]
                # print a
                names = [x for x in info if x.find(text=br_keyword[i])][0].find_all('th')
                # print names
                data = [x for x in info if x.find(text=br_keyword[i])][0].findAll('td')
                # print data
                break
        if names==data==[]: return {}
    except:
        print("Error: does not have this part.")
        return {}
    names_list = []
    data_list = []
    for name in names[1:]:
        names_list.append(name.text)
    for d in data:
        data_list.append(d.text.strip().replace('\r\n', ''))
    if len(data_list) == 0:
        return {}
    dict_ba = dict(zip(names_list,data_list))
    return dict_ba

def get_dict_list(pageSoup, key_list, *br_keyword):
    # *keyword_tuple: for names and data. a tuple like this : ([]).
    # 目前用到的省份：河北，上海，安徽，青海，云南，湖南，湖北，河南，广西，新疆(len(br_keyword)=2)。
    try:
        if br_keyword[0]==[""]:
            data = pageSoup.findAll('td')
        else:
            info = pageSoup.find(id = br_keyword[0])
            data = info.findAll('td')
    except:
        # print("Error: does not have this part.")
        return []
    data_list = []
    for d in data:
        if len(br_keyword)>=2 and (re.search(br_keyword[1],str(d)))!= None:
            data_list.append(d.find(id=re.compile("beforeMore")).text.strip().replace('\r', '').replace('\n', '').replace(u'收起更多', '').replace('\t', ''))
        else:
            data_list.append(d.text.strip().replace('\r', '').replace('\n', '').replace('\t', ''))
    if len(data_list) == 0:
        return []
    dict_ba_list = []
    while data_list!=[]:
        dict_ba = dict(zip(key_list,data_list[0:len(key_list)]))
        dict_ba_list.append(dict_ba)
        data_list = data_list[len(key_list):]
    return dict_ba_list

def get_dict_list_2(pageSoup, *br_keyword):
    # 目前用到的省份：辽宁，山东，吉林。
    dict_ba_list = []
    p = br_keyword[0]
    b = re.search(p,str(pageSoup))
    if b != None:
        s = b.group()
        if len(s)>120:
            s = s.split("]",-1)[0]+"]"
            if len(s.split("["))>1:
                s = "["+s.split("[")[1]
                dict_ba_list = json.loads(s)
    return dict_ba_list

