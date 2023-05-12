#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
from typing import List, Any
import matplotlib.pyplot as plt
import os

def lineChart(datas: List[List], index: List, columns):
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
        plt.show()
    except Exception as e:
         print(e)


def barChart( datas: List ,
              index: List,
              columns: List):
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
     # lineChart([[3], [1], [3], [4], [2]], ["5/5", "5/8", "5/9", "5/10", "5/11"], ["New dbgpt users"])
     lineChart([3, 1, 3, 4, 2], ['2023-05-09', '2023-05-05', '2023-05-08', '2023-05-10', '2023-05-11'], ["dbgpt_user"])
    # print(tidb_sql_executor('show databases;'))

     # barChart(np.random.randn(5, 2), [1, 2, 3, 4, 5], ['now', 'last'])
     # barChart_excutor()
