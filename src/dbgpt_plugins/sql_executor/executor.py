#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pymysql
import pymysql.cursors

def get_conn():
    return pymysql.connect(
        host='127.0.0.1',
        port=int('2883'),
        user='mock',
        password='mock',
        database='mock',
        charset='utf8mb4',
        ssl_ca=None,
    )

def ob_sql_executor(sql: str):
    try:
        ## TEST
        # sql = "SELECT DATE(gmt_create) AS day, COUNT(*) AS count FROM dbgpt_users WHERE gmt_create >= DATE_SUB(NOW(), INTERVAL 10 DAY) GROUP BY day;"
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        field_names = tuple(i[0] for i in cursor.description)
        result = list(result)
        result.insert(0, field_names)
        return result
    except pymysql.err.ProgrammingError as e:
        return str(e)

if __name__ == '__main__':
    # lineChart(np.random.randn(5, 2), [1, 2, 3, 4, 5], ['now', 'last'])
     print(ob_sql_executor('show databases;'))
