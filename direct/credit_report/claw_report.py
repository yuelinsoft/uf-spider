#coding=utf-8
import re
from re import error
import os
from lxml import etree
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
class Claw(object):
    _report_id=None  #报告ID
    @classmethod
    def person(cls):
        """
         个人基本信息查询
        :return:list
        """
        #判断公共记录是否有数据，如果有则抛出异常
        loss_flag=Claw.inspectLoss()
        loss_flag=1 if loss_flag==2000 else 0
        item=dict()
        item_date_keys=('report_id','query_time','report_time')
        report_date_path = '//div[@align="center"]/div/table/tr[2]/td/table[1]/tbody/tr[2]/td/strong/text()'
        report_text=spider.gettext(report_date_path)
        for index,value in enumerate(report_text):
            text=str(value.strip())
            item[item_date_keys[index]]=re.search(r'(\d.*\d)',text).group()

        #姓名，证件类型，证件号码，婚否
        #/html/body/div/div/table/tbody/tr[2]/td/table[2]/tbody/tr/td[1]/strong
        person_path='//div[@align="center"]/div/table/tr[2]/td/table[2]/tbody/tr/td/strong/text()'
        person_text=spider.gettext(person_path)
        if len(person_text)==4:
            item['name']=str(person_text[0]).strip().lstrip('姓名:').lstrip('： ').decode('utf-8')
            item['id_type']=str(person_text[1]).strip().lstrip('证件类型:').lstrip('：').decode('utf-8')
            item['id_card']=str(person_text[2]).strip().lstrip('证件号码：').decode('utf-8')
            item['marriage']=str(person_text[3]).strip().decode('utf-8')

        Claw._report_id=item['report_id']  #报告ID
        item['loss_flag']=loss_flag
        return item

    #解析信息概要的数据
    @classmethod
    def get_personinfo(cls):
        item=dict()
        info_item=list()
        #for i in range(4):

        public_path='//div[@align="center"]/div/table/tr[2]/td/table[4]/tr[3]/td/table/tbody/tr/td/table/tbody'
        for i in range(1,4):
            #1.loan_type贷款类型
            infopath=public_path+'/tr[1]/td/text()'
            info_texts=spider.gettext(infopath)
            item['loan_type']=str(info_texts[i].strip()).decode('utf-8')

            #2.accouts 账户数
            accountspath=public_path+'/tr[2]/td/text()'
            accounts_texts=spider.gettext(accountspath)
            item['accounts']=str(accounts_texts[i].strip())

            #3.no_cancel_amounts  未结清/未销户账户数
            no_cancel_path=public_path+'/tr[3]/td/text()'
            no_cancel_texts=spider.gettext(no_cancel_path)
            item['no_cancel_amounts']=str(no_cancel_texts[i].strip())

            #4.发生过逾期的账户数
            overdue_amounts_path=public_path+'/tr[4]/td/text()'
            overdue_texts=spider.gettext(overdue_amounts_path)
            item['overdue_amounts']=str(overdue_texts[i].strip())

            #5.发生过90天以上逾期的账户数
            overdue_90_amounts_path=public_path+'/tr[5]/td/text()'
            overdue_90_texts=spider.gettext(overdue_90_amounts_path)
            item['overdue_90_amounts']=str(overdue_90_texts[i].strip())

            #6.为他人担保笔数
            bond_path=public_path+'/tr[6]/td/text()'
            bond_texts=spider.gettext(bond_path)
            item['bond_amounts']=str(bond_texts[i].strip())

            item['report_id'] = Claw._report_id
            info_item.append(item)
            item=dict()
        return info_item


    @classmethod
    def query(cls):
        """
        查询机构个人查询记录明细
        :return:list
        """
        #机构查询
        query_items=list()
        item_query_keys=('query_id','query_time','query_operator','query_reason')

        try:
            query_path = '//div[@align="center"]/div/table/tr[2]/td/table[7]/tbody/tr'
            # 获得tr元素对象
            trs_Element= spider.gettext(query_path)
            for tr in trs_Element[3:-1]:
                result=list()
                #获得td元素文本
                results=tr.xpath('td/text()')
                for res in results:
                    result.append(res.strip())

                item=dict(zip(item_query_keys,result))
                item['type']=1 #1means agency's query
                item['report_id']=Claw._report_id
                query_items.append(item)

        except IndexError:
            #如果没有查询记录返回自定义信息
            item=dict()
            item['type'] = 1
            item['report_id'] = Claw._report_id
            item['query_operator']='无机构查询记录'
            query_items.append(item)

        except UnicodeEncodeError:
            pass

        #个人查询
        try:
            query_person_path = '//div[@align="center"]/div/table/tr[2]/td/table[8]/tbody/tr'
            trs_Element=spider.gettext(query_person_path)
            for tr in trs_Element[3:-1]:
                result=list()
                results=tr.xpath('td/text()')
                for res in results:
                    result.append(res.strip())
                item=dict(zip(item_query_keys,result))
                item['type']=0 #0 means personal query
                item['report_id']=Claw._report_id
                query_items.append(item)

        except IndexError:
            #如果发生异常表示没有个人查询记录写入信息
            item = dict()
            item['type'] = 1
            item['report_id'] = Claw._report_id
            item['query_operator'] = '无个人查询记录'
            query_items.append(item)
        except UnicodeEncodeError:
            pass
        return query_items
    #end

    @classmethod
    def credit(cls):
        """
        信用卡账户明细
        :return:
        """
        item=dict()
        card_items=list()

        try:
            #信用卡
            title_path = '//div[@align="center"]/div/table/tr[2]/td/span[1]/strong/text()'
            title = spider.gettext(title_path)[0].strip()
            overdue_path = '//div[@align="center"]/div/table/tr[2]/td/ol[1]/li/text()'
            over_list = spider.gettext(overdue_path)

            for over in over_list:
                over = str(over.strip())

                # 使用正则表达式匹配逾期的数据
                item['release_date'] = re.search(r'(^2.*日)', over).group(1).decode('utf-8')  # 2016年3月21日
                item['bank'] = re.search(r'日(.*行)', over).group(1).decode('utf-8')  # 招商银行
                item['card_type'] = re.search(r'的(.*卡)', over).group(1).decode('utf-8')  # 贷记卡
                item['account_type'] = re.search(r'\（(.*)\）', over).group(1).decode('utf-8')  # 人们币账户
                item['due_date'] = re.search(r'截至(.*?月)', over).group(1).decode('utf-8')  # 2016年10月
                #判断是否已销户
                try:
                    result=re.search(r'(已销户)', over).group(1).decode('utf-8')
                    item['is_cancel']=True
                except:
                    item['is_cancel']=False
                try:
                    item['credit_amount'] = re.search(r'信用额度(.*?)，', over).group(1).decode('utf-8')  # 10000
                except:
                    item['credit_amount']=0
                #判断信用卡是否激活
                try:
                    re.search(r'(尚未激活)', over).group(1).decode('utf-8')  # 10000
                    item['is_activate'] =False
                except:
                    item['is_activate']=True
                try:
                    item['used_amount'] = re.search('已使用额度(\d+,\d*)', over).group(1).decode('utf-8')  # 0
                except:
                    item['used_amount']=0
                # 增加一个逾期月数的字段
                try:
                    item['due_months'] = re.search('最近5年内有(\d+)', over).group(1).decode('utf-8')
                except Exception:
                    item['due_months']=0

                item['report_id'] = Claw._report_id  # 添加report_id
                card_items.append(item)
                item = dict()

        except (IndexError, AttributeError):
            card_items=list()
            return card_items
        except UnicodeEncodeError:
            print UnicodeEncodeError
        return card_items
    #end

    #购房贷款
    @classmethod
    def homeloan(cls):
        item=dict()
        loan_items=list()
        #如果客户没有存在购房贷款获取不到信息，应该返回
        try:
            title_path = '//div[@align="center"]/div/table/tr[2]/td/span[2]/strong/text()'
            home_title = spider.gettext(title_path)[0].strip()
            if home_title==u'购房贷款':
                loan_path_home = '//div[@align="center"]/div/table/tr[2]/td/ol[2]/li/text()'
                loan_home_texts=spider.gettext(loan_path_home)
                for home_text in loan_home_texts:
                    home_text=str(home_text.strip())
                    #print home_text
                    item['release_date'] = re.search(r'(^2.*?日)',home_text).group(1).decode('utf-8')  # 2016年3月21日
                    item['bank'] = re.search(r'日(.*)发放的',home_text).group(1).decode('utf-8')  # 招商银行
                    item['loan_amount'] = re.search(r'的(.*?元)', home_text).group(1).decode('utf-8')  # 229,000元
                    item['loan_type'] = re.search(r'\（人民币\）(.*?)贷款', home_text).group(1).decode('utf-8')
                    try:
                        clean_date=re.search(r'，(2.*?月)已结清',home_text).group(1).decode('utf-8') # 是否已结清？
                        item['clean_date'] = clean_date
                    except:
                        item['clean_date']=None
                    loan_items.append(item)
                    item=[]
                return loan_items
            else:
                loan_items=[]
                return loan_items
        except IndexError:
            loan_items=list()
            return loan_items
    #end
#其他贷款
    @classmethod
    def othloan(cls):
        #其他贷款
        #因为存在房屋贷款与没有存在房屋贷款的人，其他贷款的存在路径是不一样的，所以需要做判断
        #如果没有存在其他贷款则要返回

        try:
            title_path_n = '//div[@align="center"]/div/table/tr[2]/td/span[2]/strong/text()'
            titlen = spider.gettext(title_path_n)[0].strip()

            #不存在房屋贷款的其他贷款详情路径
            loan_path_n = '//div[@align="center"]/div/table/tr[2]/td/ol[2]/li/text()'

            #存在房屋贷款的其他贷款详情路径
            try:
                loan_path_y = '//div[@align="center"]/div/table/tr[2]/td/ol[3]/li/text()'
                title_path_y = '//div[@align="center"]/div/table/tr[2]/td/span[3]/strong/text()'
                titley = spider.gettext(title_path_y)[0].strip()
            except:
                loan_path_y=None
                title_path_y=None
                titley=None

            if titlen==u'其他贷款':
                loan_path=loan_path_n
                othloan=Claw.getothloan_text(loan_path)
                return othloan

            elif titley==u'其他贷款':
                loan_path=loan_path_y
                othloan=Claw.getothloan_text(loan_path)
                return othloan

        except IndexError:
            oth_loan_items = list()
            return oth_loan_items

#获取其他贷款详情的代码
    @staticmethod
    def getothloan_text(loan_path):
        item = dict()
        oth_loan_items = list()
        loan_texts = spider.gettext(loan_path)
        try:
            for loan in loan_texts:
                loan = str(loan.strip())
                # 使用正则表达式匹配逾期的数据
                item['release_date'] = re.search(r'(^2.*?日)', loan).group(1).decode('utf-8')  # 2016年3月21日
                item['bank'] = re.search(r'日(.*)发放的', loan).group(1).decode('utf-8')  # 招商银行
                item['loan_amount'] = re.search(r'的(.*?元)', loan).group(1).decode('utf-8')  # 229,000元
                item['loan_type'] = re.search(r'\（人民币\）(.*?)，', loan).group(1).decode('utf-8')  # 个人消费贷款
                try:
                    clean_date=re.search(r'，(2.*?月)已结清',loan).group(1).decode('utf-8') # 是否已结清？
                    item['clean_date'] = clean_date
                except:
                    item['clean_date']=None
                try:
                    item['end_date'] = re.search(r'，(.*?)到期', loan).group(1).decode('utf-8')  # 2018年5月27日
                except:
                    item['end_date']=None

                try:
                    item['due_date'] = re.search(r'截至(.*?月)', loan).group(1).decode('utf-8')  # 2016年10月
                except:
                    item['due_date']=None
                try:
                    item['remain_amount'] = re.search(r'余额(\d+,\d*)', loan).group(1).decode('utf-8')  # 余额144,059，
                except:
                    item['remain_amount']=0
                try:
                    item['overdue_amount'] = re.search(r'逾期金额(.*?)。', loan).group(1).decode('utf-8')  # 8,372。
                except:
                    item['overdue_amount'] = 0
                try:
                    item['overdue_months'] = re.search(r'最近5年内有(\d*)个月处于逾期状态', loan).group(1).decode('utf-8')  # 8,372。
                except:
                    item['overdue_months'] = 0
                oth_loan_items.append(item)
                item=dict()
            return  oth_loan_items
        except (IndexError, AttributeError):
            print IndexError
        except UnicodeEncodeError:
            print UnicodeEncodeError
#end
    @classmethod
    def inspectLoss(cls):
        """
        -判断公共记录是否存在欠税记录
        :return:
        """

        loss_path='//div[@align="center"]/div/table/tr[2]/td/table[5]/tbody/tr[2]/td/strong/text()'
        loss_text=spider.gettext(loss_path)
        text=str(loss_text[0].strip())

        try:
            re.match(r'(系统中没有您最近5年内的欠税记录)',text).group()
            return 4000
        except AttributeError:
            return 2000
#end
#获得源代码，爬取数据

class spider(object):
    html_path=None
    @classmethod
    def gettext(cls,textpath):
        if os.path.exists(spider.html_path):
            with open(spider.html_path, 'r') as f:
                text = f.read().decode('utf-8')
            selector = etree.HTML(text)
            if isinstance(selector,etree._Element):
                results = selector.xpath(textpath)
                return results

    @classmethod
    def clawReport(cls):
        person=Claw.person() #个人基本信息
        personinfo=Claw.get_personinfo()  #个人信用信息概要
        card=Claw.credit()  #信用卡记录明细
        query=Claw.query()  #机构、个人查询记录明细表
        homeloan=Claw.homeloan()
        othloan=Claw.othloan()#查询其他贷款

        return dict(
            person=person,
            personinfo=personinfo,
            card=card,
            query=query,
            homeloan=homeloan,
            loanoth=othloan
       )

def controlSpider(html):
    spider.html_path=html
    spider_data=spider.clawReport()
    return spider_data

if __name__=="__main__":
    b='13480712125.html'
    controlSpider(b)




