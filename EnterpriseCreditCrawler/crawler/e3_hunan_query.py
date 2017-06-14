# -*- coding:utf-8 -*-
# author: 'KEXH'
from common import conf,common
try:
    from StringIO import StringIO
    from BytesIO import BytesIO
except ImportError:
    from io import StringIO, BytesIO
import requests
import re
import time
Session = requests.Session()

def get_data_token():
    url = 'http://gsxt.hnaic.gov.cn/notice/'
    headers = {
        'Host': 'gsxt.hnaic.gov.cn',
        # 'X-Forwarded-For': '8,8,8,8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0'
    }
    req = Session.get(url, headers=headers, timeout=15)
    content = req.content.decode('utf-8')
    # 用正则表达式来提取token
    pattern = '.{8}-.{4}-.{4}-.{4}-.{12}'
    token = re.search(pattern, content).group()
    return token


# 拿html页面
def get_html(key, token):
    url = 'http://gsxt.hnaic.gov.cn/notice/search/ent_info_list'
    headers = {
        'Host': 'gsxt.hnaic.gov.cn',
        # 'X-Forwarded-For': '8,8,8,8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0',
        'Referer': 'http://gsxt.hnaic.gov.cn/notice/'
    }
    data = {
        'captcha': '1',
        'condition.keyword': key,
        'searchType': '1',
        'session.token': token
    }
    req = Session.post(url, headers=headers, data=data, verify=False)
    content = req.content.decode('utf-8')
    return content

def main(name):
    token = get_data_token()
    # print token
    listPage = get_html(name, token)
    if u'出错了' in listPage:
        raise ValueError ('WebsiteDown')
    else:
        result_list = common.parse_url(listPage, 'div', 'link')
        if result_list == None:
            return main(name)
        else:
            return result_list

if __name__ == '__main__':
#     namelist = [
# '武陵区鑫金诺郎烤肉店',
# '中共汨罗市委统一战线工作部',
# '常德市武陵区金都盛世商务酒店',
# '汨罗市水务局',
# '岳阳市云溪宏图彩印厂',
# '华容县公安局三封寺派出所',
# '岳阳市新公共交通总公司',
# '岳阳市岳阳楼区城陵矶街道办事处',
# '岳阳县水务局',
# '胜美达电机（常德）有限公司',
# '岳阳市昌宏科新器械有限公司',
# '华容县中医医院',
# '桃源县钰棁电子厂',
# '湖北祥瑞丰生态果业有限公司武汉分公司',
# '鼎城区人民政府蔬菜办公室',
# '南宁帝锦雄商贸有限公司',
# '临湘大市场',
# '岳阳市公交交通总公司',
# '汉寿县明明港货店',
# '汉寿县聂家桥乡宏盛电子厂',
# '石门县宇洲商贸有限公司',
# '石门县金利装饰材料总汇',
# '津市市鹏飞飞烟酒商行',
# '安乡县岳峰化工经营部',
# '平江县新海贝儿室内拓展亲子乐园',
# '常德市天勤劳务信息咨询有限公司',
# '二号菜馆',
# '石门县鸿宇农产品贸易有限公司',
# '岳阳县交通工程质量和安全监督管理站',
# '中国石化销售有限公司湖南常德石门石油分公司',
# '湖南北斗速达物流有限公司',
# '临湘市粮食局',
# '华容插旗中心小学',
# '常德市顺强市容管理有限公司',
# '合肥意标商贸有限公司',
# '南宁市桂佳酒店用品有限公司',
# '史美娥常德市鼎城区玉霞街道鼎城社区桥南市场4c1128门面',
# '广西城建咨询有限公司',
# '汉寿县众友移动专营店',
# '汨罗市自来水公司',
# '广西路易西餐饮投资有限公司',
# '南宁裕成五星印务有限公司',
# '岳阳县第八中学',
# '常德市鼎城区自来水公司',
# '岳阳天宇环保节能设备有限公司',
# '岳阳市君山区水产养殖场',
# '平江县艺成艺术团'
#                  ]
    namelist = ["腾讯"]
    for name in namelist:
        url_list = main(name)
        if len(url_list)>0:
            print "'%s',#%s"%(url_list[0],name)
            # time.sleep(15)