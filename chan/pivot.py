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
        previous_zone = None
        index = 4
        while index < len(data):
            previous = self._get_item(data, index - 4)
            current = self._get_item(data, index - 3).copy()

            # 计算中枢区间
            zone = self._get_zone(data, index - 3, 4)

            # 判断中枢是否成立
            if self._is_zone(zone, previous_zone, previous):
                # 中枢扩展
                while index < len(data) - 2:
                    next_zone = self._get_zone(data, index + 1, 2)
                    # 离开中枢区间，则结束
                    if self._out_of_range(zone, next_zone):
                        break
                    index += 2

                # 保存中枢
                last = self._get_item(data, index).copy()
                if self._is_top(current):
                    current["High"] = zone["high"]
                    last["Low"] = zone["low"]
                else:
                    current["Low"] = zone["low"]
                    last["High"] = zone["high"]

                self._keep_item(pivots, current)
                self._keep_item(pivots, last)
                previous_zone = zone
                index += 4
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

    def _is_zone(self, zone, previous_zone, previous):
        return (zone["high"] > zone["low"]
                and (self._is_top(previous)
                     and (previous_zone is None or zone["low"] < previous_zone["low"])
                     and previous["High"] > zone["low"]
                     or self._is_bottom(previous)
                     and (previous_zone is None or zone["high"] > previous_zone["high"])
                     and previous["Low"] < zone["high"]))

    @staticmethod
    def _get_zone(data, index, count):
        segments = data.iloc[index: index + count]
        return {"high": segments["High"].min(), "low": segments["Low"].max()}

    # 离开中枢
    @staticmethod
    def _out_of_range(zone, next_zone):
        return (next_zone["high"] < zone["low"] or next_zone["high"] > zone["high"]
                and next_zone["low"] < zone["low"] or next_zone["low"] > zone["high"])

    # 中枢重叠
    @staticmethod
    def _cross_range(zone, next_zone):
        return next_zone["high"] > zone["low"] and next_zone["low"] < zone["high"]

    # 计算中枢区间
    def _get_range(self, current, last):
        high = current["High"] if self._is_top(current) else last["High"]
        low = current["Low"] if self._is_bottom(current) else last["Low"]
        return {"high": high, "low": low}


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
