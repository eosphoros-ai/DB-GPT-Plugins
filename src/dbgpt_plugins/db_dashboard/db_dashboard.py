import os
import pymysql
import pymysql.cursors
import duckdb
import pandas as pd
import base64
import io
import matplotlib
import seaborn as sns
import mpld3

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties


print("Now Work DIr：", os.getcwd())
db_type = os.getenv("DB_TYPE", "DUCKDB")
database = os.getenv("DB_DATABASE", "gpt-user")
default_db_path = os.path.join(os.getcwd(), "mock_datas")
duckdb_path = os.getenv("DB_DUCKDB_PATH", default_db_path + "/db-gpt-test.db")
font_paht = os.path.join(os.getcwd(), "fonts")


def get_conn():
    try:
        if db_type and db_type == "MYSQL":
            return pymysql.connect(
                host=os.getenv("DB_HOST", "127.0.0.1"),
                port=int(
                    os.getenv("DB_PORT", 3306),
                ),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", "aa123456"),
                database=os.getenv("DB_DATABASE", "gpt-user"),
                charset="utf8mb4",
                ssl_ca=None,
            )
        elif db_type == "DUCKDB":
            return duckdb.connect(duckdb_path)
        else:
            raise ValueError("Not Support Db Type!" + db_type)

    except Exception as e:
        print("Database connection exception!" + str(e))
        raise ValueError("Database connection exception！" + str(e))


def db_schemas():
    conn = get_conn()
    if db_type == "DUCKDB":
        return __duckdb_schemas(conn)
    else:
        return __mysql_schemas(conn)


def __mysql_schemas(connect):
    _sql = f"""
                select concat(table_name, "(" , group_concat(column_name), ")") as schema_info from information_schema.COLUMNS where table_schema="{database}" group by TABLE_NAME;
          """
    with connect.cursor() as cursor:
        cursor.execute(_sql)
        results = cursor.fetchall()
    print("__mysql_schemas:" + str(results))
    if not results:
        raise ValueError(
            "No table structure information was obtained！" + os.getenv("DB_DATABASE")
        )
    return results


def __duckdb_schemas(connect):
    # 获取所有表的名称
    tables = connect.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    table_infos = []
    # 遍历所有表，获取其结构信息
    for table_name in tables:
        columns = []
        table_info = connect.execute(f"PRAGMA table_info({table_name[0]})").fetchall()
        for col_info in table_info:
            columns.append(col_info[1])
        columns_str = ",".join(columns)
        table_infos.append(f"({table_name[0]}({columns_str}));")
    if not table_infos:
        raise ValueError("No table structure information was obtained！" + duckdb_path)
    return "".join(table_infos)


def line_chart_executor(title: str, sql: str):
    df = pd.read_sql(sql, get_conn())
    columns = df.columns.tolist()
    if df.size <= 0:
        raise ValueError("No Data！" + sql)

    font = FontProperties(fname=font_paht + "/SimHei.ttf")
    plt.rcParams["font.family"] = ["sans-serif"]
    plt.rcParams["font.sans-serif"] = [font.get_name(), "Arial"]
    # fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    # ax.plot(df[columns[0]].tolist(), df[columns[1]].tolist())
    # ax.set_xlabel(columns[0])
    # ax.set_ylabel(columns[1])
    # ax.set_title(title)

    sns.set(style="ticks", color_codes=True)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    sns.lineplot(df, x=columns[0], y=columns[1])
    plt.title(title)

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode("ascii")

    html = f"""<img style='max-width: 120%; max-height: 80%;'  src="data:image/png;base64,{data}" />"""
    # with open('line_chart.html', 'w') as file:
    #     file.write(html)

    return html


def current_dir():
    return os.path.dirname(os.path.abspath(__file__))


def histogram_executor(title: str, sql: str):
    df = pd.read_sql(sql, get_conn())
    columns = df.columns.tolist()
    font = FontProperties(fname=font_paht + "/SimHei.ttf")
    if df.size <= 0:
        raise ValueError("No Data！" + sql)
    plt.rcParams["font.family"] = ["sans-serif"]
    plt.rcParams["font.sans-serif"] = [font.get_name(), "Arial"]
    rc = {"font.sans-serif": "SimHei", "axes.unicode_minus": False}
    sns.set(context="notebook", style="ticks", color_codes=True, rc=rc)
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    sns.barplot(df, x=columns[0], y=columns[1])
    plt.title(title)
    # fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    # ax.bar(df[columns[0]].tolist(), df[columns[1]].tolist())
    # ax.set_xlabel(columns[0], fontproperties=font)
    # ax.set_ylabel(columns[1])
    # ax.set_title(title, )

    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=100)
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode("ascii")

    html_img = f"""<img style='max-width: 120%; max-height: 80%;'  src="data:image/png;base64,{data}" />"""

    # with open('bar_chart.html', 'w') as file:
    #     file.write(html_img)

    return html_img


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
        return str("SQL:" + sql + "Execute Exception！," + str(e))


if __name__ == "__main__":
    # print(line_chart_executor('TEST',
    #                          "SELECT user.city, COUNT(tran_order.order_no) AS order_count FROM user LEFT JOIN tran_order ON user.name = tran_order.user_name GROUP BY user.city LIMIT 5"))
    print(db_schemas())
    # print(db_schemas())
