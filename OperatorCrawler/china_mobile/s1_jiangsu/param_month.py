#coding=utf-8

import datetime
import calendar

def getStrMonth(month): # 将月份转为两位的字符串

    month = str(month)
    month = month if len(month) == 2 else '0'+month
    return month
# end

def getMonthSeq():   # 获得近6个月的时间,格式:年+月(两位), demo：201607是字符串

    seq = list()
    today = datetime.date.today()
    year = today.year
    month = today.month + 1

    for i in range(6):
        if month-1 > 0:
            month -= 1
            year_month = str(year) + getStrMonth(month)
        else:
            year -= 1
            month = 12
            year_month = str(year) + getStrMonth(month)
        seq.append(year_month)
    # for
    seq.reverse()
    return seq
# end

##获取某一年某一个月份有多少天
def get_days_of_month(year, mon):
    '''''
    get days of month
    '''
    return calendar.monthrange(year, mon)[1]

#获取某一年某一月的第一天
def get_firstday_of_month(year, mon):
    '''''
    get the first day of month
    date format = "YYYY-MM-DD"
    '''
    days = "01"
    if (int(mon) < 10):
        mon = "0" + str(int(mon))
    arr = (year, mon, days)
    return "-".join("%s" % i for i in arr)

#获取月份的第一天与最后一天日期
def get_lastday_of_month(year, mon):
    '''''
    get the last day of month
    date format = "YYYY-MM-DD"
    '''
    days = calendar.monthrange(year, mon)[1]
    if (int(mon) < 10):
        mon = "0" + str(int(mon))
    arr = (year, mon, days)
    return "-".join("%s" % i for i in arr)

def test(): # 调用测试
    date_seq = getMonthSeq()
    print date_seq
    for seq in date_seq:
        year=int(seq[:4])
        mon=int(seq[-2:])
        print get_firstday_of_month(year,mon)
        print get_lastday_of_month(year,mon)
    # >> ['201602', '201603', '201604', '201605', '201606', '201607']



