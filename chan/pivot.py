import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.segment import Segment
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke


# 缠论中枢类
class Pivot(Layer):

    # 生成一个时间周期的数据（构建中枢）
    def generate_interval(self, interval, data):
        # 初始化空的中枢数据集
        pivots = pd.DataFrame(columns=["High", "Low"])
        if len(data) < 2:
            return pivots

        # 遍历线段，寻找中枢
        index = 0
        while index < len(data) - 2:
            first = self._get_item(data, index)
            second = self._get_item(data, index + 1).copy()

            # 计算中枢区间
            pivot_range = self._get_range(first, second)

            step = 0
            for i in range(0, len(data) - 3 - index, 2):
                current = self._get_item(data, index + i + 2)
                after = self._get_item(data, index + i + 3)

                # 离开中枢区间，则结束
                next_range = self._get_range(current, after)
                if self._out_of_range(pivot_range, next_range):
                    break

                # 重新计算中枢区间
                pivot_range[0] = min(pivot_range[0], next_range[0])
                pivot_range[1] = max(pivot_range[1], next_range[1])

                step += 2

            if step > 2:
                # 中枢成立
                current = self._get_item(data, index + step).copy()
                if self._is_top(second):
                    second["High"] = pivot_range[0]
                    current["Low"] = pivot_range[1]
                else:
                    current["High"] = pivot_range[0]
                    second["Low"] = pivot_range[1]

                self._keep_item(pivots, second)
                self._keep_item(pivots, current)
                index += step + 1
            else:
                # 中枢不成立
                index += 1

        # 合并中枢
        index = 0
        while index < len(pivots) - 3:
            first = self._get_item(pivots, index)
            second = self._get_item(pivots, index + 1)
            third = self._get_item(pivots, index + 2)
            fourth = self._get_item(pivots, index + 3)

            first_pivot = self._get_range(first, second)
            second_pivot = self._get_range(third, fourth)

            # 中枢同方向，且有重叠，则合并中枢
            if not self._out_of_range(first_pivot, second_pivot):
                if self._is_top(first) and self._is_top(third):
                    first["High"] = min(first["High"], third["High"])
                    fourth["Low"] = max(second["Low"], fourth["Low"])
                    self._drop_item(pivots, second)
                    self._drop_item(pivots, third)
                elif self._is_bottom(first) and self._is_bottom(third):
                    first["Low"] = max(first["Low"], third["Low"])
                    fourth["High"] = min(second["High"], fourth["High"])
                    self._drop_item(pivots, second)
                    self._drop_item(pivots, third)
                else:
                    index += 2
            else:
                index += 2

        return pivots

    # 计算中枢区间
    def _get_range(self, first, second):
        high = first["High"] if self._is_top(first) else second["High"]
        low = first["Low"] if self._is_bottom(first) else second["Low"]
        return [high, low]

    # 离开中枢
    @staticmethod
    def _out_of_range(pivot_range, next_range):
        return next_range[0] < pivot_range[1] or next_range[1] > pivot_range[0]


if __name__ == '__main__':
    source = Source("AAPL")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.load_from_csv()

    stroke = Stroke(fractal)
    stroke.load_from_csv()

    segment = Segment(stroke)
    segment.load_from_csv()

    pivot = Pivot(segment)
    pivot.generate()
