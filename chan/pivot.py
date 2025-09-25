import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.segment import Segment
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke


# 缠论中枢类
class Pivot(Layer):

    def __init__(self, parent: Segment, auto_load=False, auto_save=True):
        super().__init__(parent, auto_load, auto_save)

    def load_interval(self, data):
        # 初始化空的中枢数据集
        pivots = pd.DataFrame(columns=self.columns)

        if len(data) < 5:
            return pivots

        # 遍历线段，寻找中枢
        index = 0
        while index < len(data) - 5:
            # 记录起点
            enter = self._get_item(data, index)
            start = self._get_item(data, index + 1)

            # 检查后续线段，寻找中枢
            step = 0
            for i in range(1, len(data) - 2 - index):
                first = self._get_item(data, index + i + 1)
                second = self._get_item(data, index + i + 2)

                # 计算重叠区间
                overlap_high = min(start["High"], first["High"])
                overlap_low = max(start["Low"], first["Low"])

                # 如果有重叠，继续寻找中枢
                if overlap_high >= overlap_low:
                    step = i
                    start = pd.Series({
                        "Date": first["Date"],
                        "High": overlap_high,
                        "Low": overlap_low
                    })
                else:
                    break

            # 如果找到了中枢，记录终点
            if step > 0:
                index += step
                end = self._get_item(data, index + 1)

                # 保留中枢的起点和终点
                self._keep_item(pivots, start)
                self._keep_item(pivots, end)
            else:
                index += 1

        return pivots


if __name__ == '__main__':
    source = Source("AAPL", auto_load=False)
    stick = Stick(source, auto_load=False)
    fractal = Fractal(stick, auto_load=False)
    stroke = Stroke(fractal, auto_load=False)
    segment = Segment(stroke, auto_load=False)
    pivot = Pivot(segment, auto_load=True)
