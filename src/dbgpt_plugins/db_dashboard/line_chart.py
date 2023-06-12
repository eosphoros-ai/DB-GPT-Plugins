from dashboard_base import DashBoardBase
from pyecharts.charts import Line
from pyecharts import options as opts
from pandas import DataFrame

class LineChart(DashBoardBase):

    def dash_board_sql_check(self, sql: str):
        pass

    def dash_board_data_check(self, df: DataFrame):
        pass

    def dash_board_view(self, title, x_values: [], y_name, y_values: []) -> str:
        line = Line()
        line.add_xaxis(x_values)
        line.add_yaxis(y_name, y_values)
        line.set_global_opts(title_opts=opts.TitleOpts(title=title))
        return line.render_embed()
