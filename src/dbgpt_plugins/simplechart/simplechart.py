import time

import pandas as pd
import numpy as np
from typing import List, Any
import matplotlib.pyplot as plt
import os
import datetime


def line_chart_excutor(    datas: [[]] ,
                  index: [] ,
                  columns: []=[]):
    try:
        datas_len = len(datas)
        columns_len = len(columns)
        if datas_len == 0:
            raise ValueError("数据错误")
        if datas_len != len(index):
            raise ValueError("数据长度错误")
        if columns_len != len(columns):
           raise ValueError("数据列数错误")


        df = pd.DataFrame(datas, index, columns)
        df.plot()
        new_folder_path = "../../out_files/"
        if not os.path.exists(new_folder_path):
            os.mkdir(new_folder_path)

        # now = datetime.datetime.now()
        # second = now.strftime('%Y%m%d%H%M%S%f')[:-3]
        # plt.savefig(new_folder_path + second + ".png", bbox_inches='tight')
        plt.show(block=False)
        time.sleep(60)
        plt.close("all")
    except Exception as e:
         print(e)


def bar_chart_excutor( datas: [] ,
              index: [],
              columns:[]):
    try:
        print("datas:" + datas)
        print("index:" + index)
        print("datas:" + datas)
        datas_len = len(datas)
        columns_len = len(columns)
        if datas_len == 0:
            raise ValueError("数据错误")
        if datas_len != len(index):
            raise ValueError("数据长度错误:" + datas_len + "," + len(index))
        if columns_len != len(columns):
           raise ValueError("数据列数错误")


        df = pd.DataFrame(datas, index, columns)
        df.plot(kind='barh', stacked=True)
        plt.show()
        #
        # df.plot().bar(x = 1, height =1)
        # plt.show()
    except Exception as e:
         print(e)


def barChart_excutor(data:None ={'now': [1, 3, 2, 4],
            'next': [3, 2, 4, 1]}):


    # 构造 DataFrame 对象
    df = pd.DataFrame(data)

    # 绘制堆积柱状图
    df.plot(kind='barh', stacked=True)
    plt.show()

if __name__ == '__main__':
     # line_chart_excutor([[3], [1], [3], [4], [2]], ["5/5", "5/8", "5/9", "5/10", "5/11"], ["New dbgpt users"])
     line_chart_excutor([3, 1, 3, 4, 2], ['2023-05-09', '2023-05-05', '2023-05-08', '2023-05-10', '2023-05-11'], ["dbgpt_user"])
    # print(tidb_sql_executor('show databases;'))

     # bar_chart_excutor(np.random.randn(5, 2), [1, 2, 3, 4, 5], ['now', 'last'])
     # bar_chart_excutor()
