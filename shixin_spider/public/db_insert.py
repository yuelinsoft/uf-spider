#coding=utf-8
from __future__ import absolute_import
import MySQLdb
import _mysql_exceptions
from .setting import MysqlCfg


def getDBConnection():
    # 建立连接,从setting中读取配置
    return MySQLdb.connect(
        host = MysqlCfg.host,
        user = MysqlCfg.user,
        passwd = MysqlCfg.passwd,
        db = MysqlCfg.db,
        charset = MysqlCfg.charset
    )
# end

def dbInsert(table_name, column_names, items):
    """ 插入字典列表
    :param table_name: 表名 demo: 't_shixin_valid'
    :param column_names: 列名(不包括自增的列) demo: ['column_1', column_2, ...]
    :param items: 字典列表，列表中字典对应一行
    :return: None
    """
    if not isinstance(items, (list, tuple)):
        raise ValueError(u'要插入的数据类型错误')

    rows = list()
    for item in items:
        temp = list()
        for key in column_names:
            if key in item.keys():
                temp.append(item[key])
            else:
                temp.append('')
        rows.append(temp)

    # 构造%s
    symbol = ('%s,' * len(column_names)).rstrip(',')
    # 拼凑sql语句
    sql = 'insert into {table_name}({columms})'.\
          format(table_name=table_name, columms=','.join(column_names)) \
          +' values ({symbol})'.format(symbol=symbol)

    conn = getDBConnection()
    cur = conn.cursor()
    try:
        cur.executemany(sql, rows)
    except _mysql_exceptions.IntegrityError:
        for row in rows:
            try:
                cur.execute(sql, row)
            except _mysql_exceptions.IntegrityError:
                pass
            except Exception as ex:
                print ex, row
    except Exception as ex:
        print ex
    finally:
        conn.commit()
        cur.close()
        conn.close()
# end


def _demo(row_num):
    """ 测试批量插入数据
    :param row_num: 行数（记录数）
    :return: None
    """
    import time
    table_name = 't_test'
    column_names = ('stu_id', 'stu_name', 'stu_phone', 'stu_address', 'stu_remark')
    items = [dict(stu_id=i, stu_name='name'.format(i)) for i in range(row_num)]

    t_begin = time.time()
    dbInsert(table_name, column_names, items)
    print u'结束：插入{0}条记录花费时间{1}'.format(row_num, time.time()-t_begin)
# end

if __name__ == '__main__':
    _demo(1000)

