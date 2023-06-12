from dashboard_base import DashBoardBase
from pyecharts.charts import Bar
from pyecharts import options as opts
from pandas import DataFrame

class Histogram(DashBoardBase):
    def dash_board_sql_check(self, sql: str):
        super().dash_board_sql_check(sql)

    def dash_board_data_check(self, df: DataFrame):
        super().dash_board_data_check(df)

    def dash_board_view(self, title,  x_data:[],  y_name, y_data:[]) -> str:
        # 生成图表
        bar = (
            Bar()
                .add_xaxis(x_data)
                .add_yaxis(y_name, y_data)
                .set_global_opts(title_opts=opts.TitleOpts(title=title))
        )
        return bar.render_embed()