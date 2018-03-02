import pymssql

# server    数据库服务器名称或IP
# user      用户名
# password  密码
# database  数据库名称


def excuteSel(sql):
    conn = pymssql.connect('x0216u6976777.sqlserver.rds.aliyuncs.com:3433', 'x0216u', '6976777Xx', 'flask')
    cursor = conn.cursor()
    cursor.execute(sql)
    record = cursor.fetchall()

    conn.close()
    return   record
def excuteOther(sql):
    conn = pymssql.connect('x0216u6976777.sqlserver.rds.aliyuncs.com:3433', 'x0216u', '6976777Xx', 'flask')
    cursor = conn.cursor()
    cursor.execute(sql)
    print(sql)
    conn.commit()
    conn.close()
# 也可以使用for循环来迭代查询结果
# for row in cursor:
#     print("ID=%d, Name=%s" % (row[0], row[1]))

# 关闭连接
#conn.close()