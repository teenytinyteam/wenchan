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
        index = 0
        while index < len(data) - 5:
            current = self._get_item(data, index)
            first = self._get_item(data, index + 1)
            second = self._get_item(data, index + 2)
            third = self._get_item(data, index + 3)
            fourth = self._get_item(data, index + 4).copy()

            # 计算中枢区间
            previous_range = self._get_range(current, first)
            first_range = self._get_range(first, second)
            second_range = self._get_range(third, fourth)
            pivot = self._get_cross_range(first_range, second_range)

            # 判断中枢是否成立
            if self._cross_range(pivot, previous_range) and self._cross_range(first_range, second_range):
                # 中枢扩展
                suffix = 0
                while index + suffix < len(data) - 7:
                    fifth = self._get_item(data, index + suffix + 5)
                    sixth = self._get_item(data, index + suffix + 6)
                    next_range = self._get_range(fifth, sixth)
                    # 离开中枢区间，则结束
                    if self._out_of_range(pivot, next_range):
                        break
                    suffix += 2

                # 保存中枢
                last = self._get_item(data, index + suffix + 4).copy()
                after = self._get_item(data, index + suffix + 5)
                if self._on_direction(pivot, after):
                    if self._is_top(first):
                        first["High"] = pivot["high"]
                        last["Low"] = pivot["low"]
                    else:
                        first["Low"] = pivot["low"]
                        last["High"] = pivot["high"]

                    self._keep_item(pivots, first)
                    self._keep_item(pivots, last)
                    index += suffix + 4
                else:
                    index += 1
            else:
                # 中枢不成立
                index += 1

        # 合并中枢
        index = 0
        while index < len(pivots) - 3:
            current = self._get_item(pivots, index)
            first = self._get_item(pivots, index + 1)
            first_pivot = self._get_range(current, first)

            second = self._get_item(pivots, index + 2)
            third = self._get_item(pivots, index + 3)
            second_pivot = self._get_range(second, third)

            # 中枢同方向，且有重叠，则合并中枢
            if self._cross_range(first_pivot, second_pivot):
                if self._is_top(current) and self._is_top(second):
                    current["High"] = max(current["High"], second["High"])
                    third["Low"] = min(first["Low"], third["Low"])
                    self._drop_item(pivots, first)
                    self._drop_item(pivots, second)
                elif self._is_bottom(current) and self._is_bottom(second):
                    current["Low"] = min(current["Low"], second["Low"])
                    third["High"] = max(first["High"], third["High"])
                    self._drop_item(pivots, first)
                    self._drop_item(pivots, second)
                else:
                    index += 2
            else:
                index += 2

        return pivots

    # 计算中枢区间
    def _get_range(self, current, last):
        high = current["High"] if self._is_top(current) else last["High"]
        low = current["Low"] if self._is_bottom(current) else last["Low"]
        return {"high": high, "low": low}

    # 中枢重叠
    @staticmethod
    def _cross_range(first_range, second_range):
        return (second_range["high"] > first_range["low"]
                and second_range["low"] < first_range["high"])

    # 离开中枢
    @staticmethod
    def _out_of_range(first_range, second_range):
        return ((second_range["high"] < first_range["low"]
                 or second_range["high"] > first_range["high"])
                and (second_range["low"] < first_range["low"]
                     or second_range["low"] > first_range["high"]))

    @staticmethod
    def _get_cross_range(first_range, second_range):
        return {"high": min(first_range["high"], second_range["high"]),
                "low": max(first_range["low"], second_range["low"])}

    def _on_direction(self, pivot, after):
        return (self._is_top(after) and after["High"] > pivot["high"]
                or self._is_bottom(after) and after["Low"] < pivot["low"])


class StrokePivot(Pivot):
    pass


class SegmentPivot(Pivot):
    pass


if __name__ == '__main__':
    source = Source("000001.SS")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.load_from_csv()

    stroke = Stroke(fractal)
    stroke.load_from_csv()

    strokePivot = StrokePivot(stroke)
    strokePivot.generate()

    segment = Segment(stroke)
    segment.load_from_csv()

    segmentPivot = SegmentPivot(segment)
    segmentPivot.generate()
