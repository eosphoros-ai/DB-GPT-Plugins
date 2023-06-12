import os
import pymysql
import pymysql.cursors
import duckdb
import pandas as pd



from line_chart import LineChart
from histogram import Histogram

from dotenv import load_dotenv

# Load the users .env file into environment variables
load_dotenv(verbose=True, override=True)
del load_dotenv

def get_conn():
    try:
        db_type = os.getenv("DB_TYPE", "MYSQL")
        if (db_type == "MYSQL"):
            if (db_type == "MYSQL"):
                return pymysql.connect(
                    host=os.getenv("DB_HOST", "127.0.0.1"),
                    port=int(os.getenv("DB_PORT", 3306), ),
                    user=os.getenv("DB_USER", "root"),
                    password=os.getenv("DB_PASSWORD", "aa123456"),
                    database=os.getenv("DB_DATABASE"),
                    charset='utf8mb4',
                    ssl_ca=None,
                )
        elif db_type == "DUCKDB":
            current_dir = os.path.abspath('.')
            test_db = current_dir + "db-gpt-test.db"
            return duckdb.connect(database=os.getenv("DB_PATH", test_db))
        else:
            raise ValueError("尚未支持的数据库类型" + db_type)
    except Exception as e:
        return str("数据库连接异常！" + str(e))

def db_schemas():
    conn = get_conn()
    _sql = f"""
              select concat(table_name, "(" , group_concat(column_name), ")") as schema_info from information_schema.COLUMNS where table_schema="{os.getenv("DB_DATABASE")}" group by TABLE_NAME;
          """
    with conn.cursor() as cursor:
        cursor.execute(_sql)
        results = cursor.fetchall()
    return results

def line_chart_executor(title: str, sql: str):
    df = pd.read_sql(sql, get_conn())

    columns = df.columns.tolist()

    chart: LineChart = LineChart()
    return chart.dash_board_view(title, df[columns[0]].tolist(), columns[1],  df[columns[1]].tolist())


def histogram_executor(title: str, sql: str):
    df = pd.read_sql(sql, get_conn())

    columns = df.columns.tolist()

    chart: Histogram = Histogram()
    return  chart.dash_board_view(title, df[columns[0]].tolist(), columns[1],  df[columns[1]].tolist())


def __sql_execute(sql: str, db_name: str = None):
    try:
        if db_name:
            conn = get_conn()
        else:
            conn = get_conn(db_name)
        with conn.cursor() as cursor:
            cursor.execute(sql)
            result = cursor.fetchall()
        field_names = tuple(i[0] for i in cursor.description)
        result = list(result)
        return field_names, result
    except pymysql.err.ProgrammingError as e:
        return str("SQL:" + sql + "执行异常," + str(e))


if __name__ == '__main__':
    # print(histogram_executor('测试', "SELECT users.city, COUNT(tran_order.order_id) AS order_count FROM users LEFT JOIN tran_order ON users.user_name = tran_order.user_name GROUP BY users.city LIMIT 5"))
    print(db_schemas())