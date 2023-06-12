import os
import pymysql
import pymysql.cursors
import duckdb
import pandas as pd
import base64
import io
from pyecharts.charts import Line, Bar
from pyecharts import options as opts
import matplotlib.pyplot as plt
import mpld3

from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.resources import INLINE
import numpy as np


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
                    database=os.getenv("DB_DATABASE", "gpt-user"),
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

    # # 绘制折线图
    # p = figure(title=title, x_axis_label=columns[0], y_axis_label=columns[1])
    # p.line(df[columns[0]].tolist(), df[columns[1]].tolist())
    #
    # # 生成 HTML
    # html = file_html(p, INLINE, title + 'Line Chart')
    # # 打印 HTML
    # # print(html)
    # with open('line_chart.html', 'w') as file:
    #     file.write(html)
    # return html

    # # 绘制折线图
    fig, ax = plt.subplots()
    ax.plot(df[columns[0]].tolist(), df[columns[1]].tolist())
    ax.set_xlabel(columns[0])
    ax.set_ylabel(columns[1])
    ax.set_title(title)

    # 将图表保存为二进制数据
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode('ascii')

    # 生成 HTML
    html = f'<img src="data:image/png;base64,{data}"/>'

    with open('line_chart.html', 'w') as file:
        file.write(html)

    return html
    # # 转换为 HTML 文本
    # html_text = mpld3.fig_to_html(fig)
    # print(html_text)
    # return html_text

    # line = Line()
    # line.add_xaxis(df[columns[0]].tolist())
    # line.add_yaxis(columns[1], df[columns[1]].tolist())
    # line.set_global_opts(title_opts=opts.TitleOpts(title=title))
    # line.render('report.html')
    # return line.render_embed()


def histogram_executor(title: str, sql: str):
    df = pd.read_sql(sql, get_conn())

    columns = df.columns.tolist()

    # 绘制柱状图
    fig, ax = plt.subplots()
    ax.bar(df[columns[0]].tolist(), df[columns[1]].tolist())
    ax.set_xlabel(columns[0])
    ax.set_ylabel(columns[1])
    ax.set_title(title)


    # 将图表保存为二进制数据
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode('ascii')

    # 生成 HTML
    html = f'<img src="data:image/png;base64,{data}"/>'

    with open('bar_chart.html', 'w') as file:
        file.write(html)

    return html


    # # 转换为 HTML 文本
    # html_text = mpld3.fig_to_html(fig)
    # print(html_text)
    # return html_text

    # bar = (
    #     Bar()
    #         .add_xaxis(df[columns[0]].tolist())
    #         .add_yaxis(columns[1], df[columns[1]].tolist())
    #         .set_global_opts(title_opts=opts.TitleOpts(title=title))
    # )
    # bar.render('report.html')
    # return bar.render_embed()


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
    print(line_chart_executor('测试', "SELECT users.city, COUNT(tran_order.order_id) AS order_count FROM users LEFT JOIN tran_order ON users.user_name = tran_order.user_name GROUP BY users.city LIMIT 5"))
    # print(db_schemas())
