import numpy as np
import pandas as pd

from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick


# 缠论分型类
class Fractal(Layer):

    # 生成一个时间周期的数据（分辨分型）
    def generate_interval(self, interval, data):
        # 初始化分型数据集
        fractals = pd.DataFrame(columns=["High", "Low"])
        if len(data) < 3:
            return fractals

        # 遍历线，寻找分型
        for index in range(1, len(data) - 1):
            previous = self._get_item(data, index - 1)
            current = self._get_item(data, index).copy()
            first = self._get_item(data, index + 1)

            # 如果是顶分型，则保留最高价，删除最低价
            if self._is_top_fractal(previous, current, first):
                current['Low'] = np.nan
            # 如果是底分型，则保留最低价，删除最高价
            elif self._is_bottom_fractal(previous, current, first):
                current['High'] = np.nan
            # 如果不是分型，则删除该价格，只保留位置（用于下一步笔的计算）
            else:
                current['High'] = np.nan
                current['Low'] = np.nan

            # 保留当前K线，无论是否是分型
            self._keep_item(fractals, current)

        return fractals

    # 判断是否为顶分型
    @staticmethod
    def _is_top_fractal(previous, current, first):
        return current["High"] > previous["High"] and current["High"] > first["High"]

    # 判断是否为底分型
    @staticmethod
    def _is_bottom_fractal(previous, current, first):
        return current["Low"] < previous["Low"] and current["Low"] < first["Low"]


if __name__ == '__main__':
    source = Source("002594.SZ")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.generate()
