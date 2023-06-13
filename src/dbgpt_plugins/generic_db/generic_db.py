import os
import pymysql
import pymysql.cursors


def get_conn(db_name: str = None):
    db_type = os.getenv("DB_TYPE", "MYSQL")
    if db_name == None:
        if (db_type == "MYSQL"):
            return pymysql.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(os.getenv("DB_PORT", 3306), ),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "123"),
                database=os.getenv("DB_DATABASE"),
                charset='utf8mb4',
                ssl_ca=None,
            )
        else:
            raise ValueError("尚未支持的数据库类型" + db_type)

    else:
        if (db_type == "MYSQL"):
            return pymysql.connect(
                host=os.getenv(),
                port=int('2883'),
                user='puzzle@puzzle0_1954#dev_ipay10',
                password='puzzle123',
                database=db_name,
                charset='utf8mb4',
                ssl_ca=None,
            )
        else:
            raise ValueError("尚未支持的数据库类型" + db_type)


def db_sql_executor(sql: str):
    try:
        conn = get_conn()
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        field_names = tuple(i[0] for i in cursor.description)
        result = list(result)
        result.insert(0, field_names)
        return result
    except pymysql.err.ProgrammingError as e:
        return str("SQL:" + sql + "执行异常," + str(e))


def executor_sql_in_db(db_name: str, sql: str):
    try:
        conn = get_conn(db_name)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        field_names = tuple(i[0] for i in cursor.description)
        result = list(result)
        result.insert(0, field_names)
        return result
    except pymysql.err.ProgrammingError as e:
        return str("在Db" + db_name + "中执行SQL:" + sql + "异常," + str(e))


if __name__ == '__main__':
    print(db_sql_executor('show databases;'))
