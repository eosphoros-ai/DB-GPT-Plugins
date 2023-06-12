import pandas as pd
from pandas import DataFrame

class DashBoardBase:

    def dash_board_sql_check(self, sql: str):
        pass

    def dash_board_data_check(self, df: DataFrame):
        pass

    def dash_board_view(self, df: DataFrame) -> str:
        pass
