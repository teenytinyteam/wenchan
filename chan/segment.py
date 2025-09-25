import numpy as np
import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke


# 缠论线段类
class Segment(Layer):

    def __init__(self, parent: Stroke, auto_load=False, auto_save=True):
        super().__init__(parent, auto_load, auto_save)

    def load_interval(self, data):
        # 初始化空的线段数据集
        segments = pd.DataFrame(columns=self.columns)

        if len(data) < 3:
            return segments

        # 遍历笔，寻找线段
        index = 0
        while index < len(data) - 3:
            # 记录起点
            start = self._get_item(data, index)

            # 检查后续笔，直到无法构成更长的线段
            step = 0
            for i in range(0, len(data) - 3 - index, 2):
                # 取出两笔，检查是否继续同方向运动
                first = self._get_item(data, index + i + 1)
                second = self._get_item(data, index + i + 3)
                # 如果不再同方向运动，则当前线段结束
                if (not self._go_up_and_up(first, second)
                        and not self._go_down_and_down(first, second)):
                    step = i + 1
                    break
                # 线段延续
                step = i + 3

            # 记录终点
            index += step
            end = self._get_item(data, index)

            # 保留线段的起点和终点
            self._keep_item(segments, start)
            self._keep_item(segments, end)

        return segments

    # 判断两笔是否持续向上
    @staticmethod
    def _go_up_and_up(first, second):
        if not np.isnan(first["High"]) and not np.isnan(second["High"]):
            return second["High"] >= first["High"]
        return False

    # 判断两笔是否持续向下
    @staticmethod
    def _go_down_and_down(first, second):
        if not np.isnan(first["Low"]) and not np.isnan(second["Low"]):
            return second["Low"] <= first["Low"]
        return False


if __name__ == '__main__':
    source = Source("AAPL", auto_load=False)
    stick = Stick(source, auto_load=False)
    fractal = Fractal(stick, auto_load=False)
    stroke = Stroke(fractal, auto_load=False)
    segment = Segment(stroke, auto_load=True)
