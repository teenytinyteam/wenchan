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
        if len(data) < 5:
            return pivots

        # 遍历线段，寻找中枢
        index = 4
        while index < len(data):
            before = self._get_item(data, index - 4)
            first = self._get_item(data, index - 3).copy()

            # 计算中枢区间
            segments = data.iloc[index - 3: index + 1]
            zone = {"high": segments["High"].min(), "low": segments["Low"].max()}

            # 判断中枢是否成立
            if (zone["high"] > zone["low"]
                    and (self._is_top(before) and before["High"] > zone["low"]
                         or self._is_bottom(before) and before["Low"] < zone["high"])):
                # 中枢扩展
                while index < len(data) - 2:
                    next_segments = data.iloc[index + 1: index + 3]
                    next_zone = {"high": next_segments["High"].min(), "low": next_segments["Low"].max()}
                    # 离开中枢区间，则结束
                    if self._out_of_range(zone, next_zone):
                        break
                    index += 2

                # 保存中枢
                last = self._get_item(data, index).copy()
                if self._is_top(first):
                    first["High"] = zone["high"]
                    last["Low"] = zone["low"]
                else:
                    first["Low"] = zone["low"]
                    last["High"] = zone["high"]

                self._keep_item(pivots, first)
                self._keep_item(pivots, last)
                index += 4
            else:
                # 中枢不成立
                index += 1

        # 合并中枢
        index = 0
        while index < len(pivots) - 3:
            first = self._get_item(pivots, index)
            second = self._get_item(pivots, index + 1)
            first_pivot = self._get_range(first, second)

            third = self._get_item(pivots, index + 2)
            fourth = self._get_item(pivots, index + 3)
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

    # 离开中枢
    @staticmethod
    def _out_of_range(pivot_range, next_range):
        return next_range["high"] < pivot_range["low"] or next_range["low"] > pivot_range["high"]

    # 计算中枢区间
    def _get_range(self, first, second):
        high = first["High"] if self._is_top(first) else second["High"]
        low = first["Low"] if self._is_bottom(first) else second["Low"]
        return {"high": high, "low": low}


if __name__ == '__main__':
    source = Source("002594.SZ")
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
