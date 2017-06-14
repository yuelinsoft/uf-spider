#coding=utf-8
import  MySQLdb
from ...public import getDBConnection


class Search():

    columns = 'sys_id, name, card_num, case_code, reg_date, court_name, execute_money'

    @classmethod
    def query(cls, name, card_num):
        """ 从表读取num个id,并删除该记录
        :param num: id数
        :return: IDList/[]
        """
        if isinstance(name, unicode):
            name = name.encode('utf-8')

        conn =  getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        if card_num != '':
            # 个人的处理方式
            card_num = Search.alterCardNum(card_num)
            sql = 'select {0}  from t_zhixing_valid where name = "{1}" and card_num = "{2}" '.format(Search.columns, name, card_num)
        else:
            # 公司的处理方式
            sql = 'select {0}  from t_zhixing_valid where name = "{1}"'.format(Search.columns, name)
        cur.execute(sql)
        result = cur.fetchall()
        cur.close()
        conn.commit()
        conn.close()
        return result
    # end

    @classmethod
    def alterCardNum(cls, card_num):
        if len(card_num) == 18: # 旧版身份证
            card_num = card_num[:-7] + '*'*4 + card_num[-4:]
            return card_num
        elif len(card_num) == 15:
            card_num = card_num[:-7] + '*'*4 + card_num[-4:]
            return card_num
        else:
            raise ValueError('参数错误,身份证号异常')


if __name__ == '__main__':
    print Search.query(u'上海彤新汽车销售服务有限公司', '')   # 公司
    print Search.query(u'曹俊元', '370822196702346118')     # 个人

