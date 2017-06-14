#coding=utf-8
import MySQLdb
from ...public import getDBConnection


class Search(object):
    """失信 - 实时查询用到的类"""
    columns = 'sys_id, name, age, sex, card_num, business_entity, area_name, case_code, reg_date, publish_date, gist_id, court_name,\
    gist_unit, duty, performance, disrupt_type_name, party_type_name, flag'

    @classmethod
    def query(cls, name, card_num):
        """ 查询 """
        if isinstance(name, unicode):
            name = name.encode('utf-8')

        conn =  getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)
        if card_num != '': # 个人
            card_num = Search.alterCardNum(card_num)
            sql = 'select {0}  from t_shixin_valid where name = "{1}" and card_num = "{2}" and flag = 0 '.format(Search.columns, name, card_num)
        else: # 公司
            sql = 'select {0}  from t_shixin_valid where name = "{1}" and flag = 1'.format(Search.columns, name)
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
            card_num = card_num[:-8] + '*'*4 + card_num[-4:]
            return card_num
        elif len(card_num) == 15:
            card_num = card_num[:-8] + '*'*4 + card_num[-4:]
            return card_num
        else:
            raise ValueError('参数错误,身份证号异常')


    @classmethod
    def queryRequestFailID(cls, num):
        """ 从表读取num个id,并删除该记录
        :param num: id数
        :return: IDList/[]
        """
        conn =  getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        sql = 'select sys_id from t_shixin_invalid where err_type in (1,2) and flag=1 limit {0}'.format(num)
        cur.execute(sql)
        ids = [int(item['sys_id']) for item in cur.fetchall()]

        if ids:
            sql = 'delete from t_shixin_invalid where sys_id in {0}'.format(str(tuple(ids)))
            cur.execute(sql)

        cur.close()
        conn.commit()
        conn.close()
        return ids
    # end

class Spider(object):

    @classmethod
    def updateIDstatus(cls, id_seq):
        """ 根据id列表或者tuple更新表
        :param id_seq: list or tuple
        :return: True or False
        """
        conn =  getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        if not isinstance(id_seq, (tuple,list)):
            raise ValueError(u'参数错误')

        sql = 'update t_shixin_invalid set flag=0 where sys_id in {0}'.format(str(tuple(id_seq)))

        cur.execute(sql)
        cur.close()
        conn.commit()
        conn.close()
    # end

    @classmethod
    def queryErrUnknownID(cls, num):
        """ 从表读取num个可能不存在内容的id
        :param num: id数
        :return: IDList/[]
        """
        conn =  getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        sql = 'select sys_id from t_shixin_invalid where err_type=3 and flag=1 limit {0}'.format(num)
        cur.execute(sql)
        id_seq = [int(item['sys_id']) for item in cur.fetchall()]

        cur.close()
        conn.close()
        return id_seq
    # end

    @classmethod
    def deleteErrItems(cls, id_seq):
        """ 从错误表中删除存在内容的id记录
        :param id_seq: list/tuple
        :return: None
        """
        conn =  getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        sql = 'delete from t_shixin_invalid  where sys_id in {0}'.format(str(tuple(id_seq)))
        cur.execute(sql)

        cur.close()
        conn.commit()
        conn.close()
    # end

    @classmethod
    def queryLostID(cls, start_id, end_id):
        """ 获得区间[start_id, end_Id]不在表中的记录的id
        :return: list/[]
        """
        sys_ids = list()
        conn = getDBConnection()
        cur = conn.cursor(cursorclass = MySQLdb.cursors.DictCursor)

        tables = ('t_shixin_valid', 't_shixin_invalid')
        sql = 'select sys_id from {table} where sys_id between start_id and end_id'

        for table in tables:
            cur.execute(sql.format(table=table))
            for item in cur.fetchall():
                sys_ids.append(item['sys_id'])
        cur.close()
        conn.close()
        #3307986为当前数据的最小id, 4825018为最大id
        return list(set(range(start_id, end_id+1)) - set(sys_ids))
    # end


if __name__ == '__main__':
    print Search.query(u'上海彤新汽车销售服务有限公司', '')   # 公司
    # print query(u'曹俊元', '370822196702346118')          # 个人

