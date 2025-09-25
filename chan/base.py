import os
from abc import abstractmethod, ABC
from enum import Enum
from pathlib import Path
from typing import Dict

import pandas as pd


# 时间周期级别
class Interval(Enum):
    # MIN_1 = "1m"
    # MIN_5 = "5m"
    # MIN_30 = "30m"
    # HOUR_1 = "1h"
    DAY_1 = "1d"
    # WEEK_1 = "1wk"
    # MONTH_1 = "1mo"


# 基础类
class Base(ABC):

    def __init__(self, symbol, auto_load=False, auto_save=True):
        # 股票代码
        self.symbol = symbol

        self.path = Path(__file__).parent.parent / "data" / self.symbol
        self.name = self.__class__.__name__.lower()
        self.data: Dict[str, pd.DataFrame] = {}

        if auto_load:
            self.load()
            if auto_save:
                self.save()
        else:
            self.load_from_csv()

    @abstractmethod
    def load(self):
        pass

    # 保存数据到CSV文件
    def save(self):
        os.makedirs(self.path, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(self._file_name(interval), index_label='Date')

    # 从CSV文件加载数据
    def load_from_csv(self):
        for interval in Interval:
            file_name = self._file_name(interval.value)
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
        return self.data.get(interval)

    # 生成文件名
    def _file_name(self, interval):
        return f'{self.path}/{self.name}_{interval}.csv'
