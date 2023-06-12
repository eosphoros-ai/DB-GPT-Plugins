import os
import pymysql
import pymysql.cursors
import duckdb
import pandas as pd
import base64
import io
from pyecharts.charts import Line, Bar
from pyecharts import options as opts

import mpld3
import matplotlib
import matplotlib.font_manager as fm
matplotlib.use('Agg')  # 指定使用非交互式后端
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from bokeh.embed import file_html
from bokeh.resources import INLINE
import numpy as np
from matplotlib.font_manager import FontProperties


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

    plt.rcParams['font.sans-serif'] = ['SimHei']
    # # 绘制折线图
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
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
    html = f'<img src="data:image/png;base64,{data}"  width="800" height="600"/>'

    with open('line_chart.html', 'w') as file:
        file.write(html)

    return html
    # # 转换为 HTML 文本
    # html_text = mpld3.fig_to_html(fig)
    # print(html_text)
    # return html_text
    #
    # line = Line()
    # line.add_xaxis(df[columns[0]].tolist())
    # line.add_yaxis(columns[1], df[columns[1]].tolist())
    # line.set_global_opts(title_opts=opts.TitleOpts(title=title))
    # line.render('report.html')
    # html = line.render_embed()
    # html.replace("""<script type="text/javascript" src="https://assets.pyecharts.org/assets/v5/echarts.min.js"></script>""", f"""<script type="text/javascript" >{getJsStr()}</script>""")
    #
    # return html

def current_dir():
    return os.path.dirname(os.path.abspath(__file__))

def histogram_executor(title: str, sql: str):
    df = pd.read_sql(sql, get_conn())

    columns = df.columns.tolist()
    font = FontProperties(fname=f"{current_dir()}/SourceHanSansSC-Bold.otf", size=15)

    # 绘制柱状图
    plt.rcParams['font.sans-serif'] = ['SimHei']
    fig, ax = plt.subplots(figsize=(8, 6), dpi=100)
    ax.bar(df[columns[0]].tolist(), df[columns[1]].tolist())
    ax.set_xlabel(columns[0],fontproperties=font)
    ax.set_ylabel(columns[1],fontproperties=font)
    ax.set_title(title,fontproperties=font)

    # 将图表保存为二进制数据
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    data = base64.b64encode(buf.getvalue()).decode('ascii')

    # 生成 HTML
    html_img = f'<img class="my-image" src="data:image/png;base64,{data}" width="1024" height="768"/>'
    table_style = """<style> 
      .my-image {
        width: 800px;
        height: 600px;
      }
     </style>"""
    html = f"<html><head>{table_style}</head><body>{html_img}</body></html>"
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
    # html = bar.render_embed();
    # html.replace("""<script type="text/javascript" src="https://assets.pyecharts.org/assets/v5/echarts.min.js"></script>""", f"""<script type="text/javascript" >{getJsStr()}</script>""")
    # with open('bar_chart.html', 'w') as file:
    #     file.write(html)
    # return html


def getJsStr():
    # 打开文件，指定读取模式（'r' 表示读取）
    file = open('echarts.min.js', 'r')

    # 逐行读取文件内容
    lines = file.readlines()

    # 关闭文件
    file.close()

    # 将每行文本内容合并为一个字符串
    text = ''.join(lines)
    return text

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
    print(histogram_executor('测试', "SELECT users.city, COUNT(tran_order.order_id) AS order_count FROM users LEFT JOIN tran_order ON users.user_name = tran_order.user_name GROUP BY users.city LIMIT 5"))
    # print(db_schemas())
