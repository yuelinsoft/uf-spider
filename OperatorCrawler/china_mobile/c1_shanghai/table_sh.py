#coding=utf-8

# 表名
TABEL_NAME_1 = 't_operator_user'
TABLE_NAME_2 = 't_operator_call'
TABLE_NAME_3 = 't_operator_note'

# 上海移动用户信息
KEY_CONVERT_USER = {
'name', 'sex', 'address', 'cert_type', 'cert_num',
'phone', 'company', 'province', 'city', 'product_name',
'level', 'open_date', 'balance', 'user_valid'
}

# 上海移动通话记录
LIST_CONVERT_CALL = [u'序号', u'起始时间', u'通信地点', u'通信方式', u'对方号码', u'通信时长', u'通信类型', u'套餐优惠', u'实收通信费', u'是否“新通话”']

KEY_CONVERT_CALL = {
    'call_area': [u'通话地点', u'通信地点', u'本机通话地'],
    # 'call_date': [u'通话日期', u''],##
    # 'call_time': [u'通话时分秒', u''],##
    'call_cost': [u'通话费用', u'通话费', u'实收通话费', u'实收通信费'],
    'call_long': [u'通话时长', u'通信时长'],
    'other_phone': [u'对方号码'],
    'call_type': [u'呼叫类型', u'通信方式'],
    'land_type': [u'通话类型', u'通信类型']
}

# 上海移动短信记录
LIST_CONVERT_NOTE = [u'序号', u'起始时间', u'通信地点', u'对方号码', u'通信方式', u'信息类型', u'套餐', u'通信费']

# 上海移动短信记录内容字段转换
KEY_CONVERT_NOTE = {
    # 'note_date': [u'通话日期'],
    # 'note_time': [u'通话时分秒'],
    'note_cost': [u'短信费用', u'通信费'],
    'business_type': [u'业务类型', u'信息类型'],
    'other_phone': [u'对方号码']
}


# 下面这些还没有用到

# 用户表-需要插入数据的字段
COLUMN_USER = (
    'name','sex', 'address', 'cert_type', 'cert_num',
    'phone', 'company', 'province', 'city', 'product_name',
    'level', 'open_date', 'balance', 'user_valid'
)

# 通话记录表-需要插入数据的字段
COLUMN_CALL = (
    'cert_num', 'phone', 'call_area', 'call_date',
    'call_time','call_cost', 'call_long', 'other_phone',
    'call_type', 'land_type'
)

# 短信记录表-需要插入数据的字段
COLUMN_NOTE = (
    'cert_num', 'phone', 'note_date', 'note_time',
    'note_cost', 'business_type', 'other_phone'
)