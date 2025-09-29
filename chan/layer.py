import os
from abc import ABC, abstractmethod
from enum import Enum
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


# 时间周期级别
class Interval(Enum):
    MIN_1 = "1m"
    MIN_5 = "5m"
    MIN_30 = "30m"
    HOUR_1 = "1h"
    DAY_1 = "1d"
    WEEK_1 = "1wk"
    MONTH_1 = "1mo"


# 抽象层基类
class Layer(ABC):

    def __init__(self, parent):
        if isinstance(parent, Layer):
            self.symbol = parent.symbol
            self.parent = parent
        else:
            self.symbol = parent
            self.parent = None

        self.path = Path(__file__).parent.parent / "data" / self.symbol
        self.name = self.__class__.__name__.lower()

        self.data: Dict[str, pd.DataFrame | None] = {interval.value: None for interval in Interval}

    # 生成数据
    def generate(self, auto_save=True):
        for interval in Interval:
            self.data[interval.value] = self.generate_interval(interval, self.parent.data[interval.value])
        if auto_save:
            self.save()

    # 生成一个时间周期的数据
    @abstractmethod
    def generate_interval(self, interval, data):
        pass

    # 保存数据到CSV文件
    def save(self):
        os.makedirs(self.path, exist_ok=True)
        for interval in Interval:
            data = self.get_data(interval)
            if data is not None:
                data.to_csv(self._file_name(interval), index_label='Date')

    # 从CSV文件加载数据
    def load_from_csv(self):
        for interval in Interval:
            file_name = self._file_name(interval)
            if os.path.exists(file_name):
                try:
                    data = pd.read_csv(file_name, index_col=0, parse_dates=True)
                    self.data[interval.value] = data
                except Exception as e:
                    print(f"Error loading {file_name}: {e}")
            else:
                print(f"File {file_name} does not exist.")

    # 获取指定周期的数据
    def get_data(self, interval):
        return self.data.get(interval.value)

    # 生成文件名
    def _file_name(self, interval):
        return f'{self.path}/{self.name}_{interval.value}.csv'

    # 获取数据项
    @staticmethod
    def _get_item(data, index):
        return data.iloc[index]

    # 保存数据项
    @staticmethod
    def _keep_item(data, item, columns=None):
        if columns is not None:
            data.loc[item.name] = item[columns]
        else:
            data.loc[item.name] = item

    # 删除数据项
    @staticmethod
    def _drop_item(data, item):
        data.drop(item.name, inplace=True)

    # 判断是否为顶分型
    @staticmethod
    def _is_top(item):
        return np.isnan(item["Low"]) and not np.isnan(item["High"])

    # 判断是否为底分型
    @staticmethod
    def _is_bottom(item):
        return np.isnan(item["High"]) and not np.isnan(item["Low"])
