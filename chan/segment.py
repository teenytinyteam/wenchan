import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke


# 缠论线段类
class Segment(Layer):

    # 生成一个时间周期的数据（划分线段）
    def generate_interval(self, interval, data):
        # 初始化空的线段数据集
        segments = pd.DataFrame(columns=["High", "Low"])
        if len(data) == 0:
            return segments

        # 用于存储短线段的临时列表
        short_segments = []

        # 遍历笔，寻找线段
        index = 0
        while index < len(data) - 3:
            start = self._get_item(data, index)

            # 检查后续笔，直到无法构成更长的线段
            step = 0
            for i in range(0, len(data) - 3 - index, 2):
                first = self._get_item(data, index + i + 1)
                third = self._get_item(data, index + i + 3)
                # 如果第三笔不延续第一笔的走势，则当前线段结束
                if not self._go_up_and_up(first, third) and not self._go_down_and_down(first, third):
                    step = i + 1
                    break
                # 线段延续
                step = i + 3

            # 保存完整线段和短线段
            short_segments.append([index, start])

            # 记录终点
            index += step
            end = self._get_item(data, index)

            # 保留线段的起点和终点
            self._keep_item(segments, start)
            self._keep_item(segments, end)

            # 合并之前的短c
            if step >= 3:
                short_segments = self._merge_short_segments(segments, short_segments)

        return segments

    # 判断两笔是否持续向上
    def _go_up_and_up(self, first, second):
        if self._is_top(first) and self._is_top(second):
            return second["High"] >= first["High"]
        return False

    # 判断两笔是否持续向下
    def _go_down_and_down(self, first, second):
        if self._is_bottom(first) and self._is_bottom(second):
            return second["Low"] <= first["Low"]
        return False

    # 合并短线段
    def _merge_short_segments(self, segments, short_segments):
        if len(short_segments) < 2:
            return []

        # 取出首尾两个线段
        first = short_segments[0][1]
        last = short_segments[-1][1]

        # 如果首尾都是向下笔，则保留最高价的笔，删除其他笔。等同于将所有短线段合并到前后完整的线段
        if self._is_bottom(first) and self._is_bottom(last):
            max_high_item = max(short_segments, key=lambda x: x[1]["High"])
            for item in short_segments:
                if item is not max_high_item:
                    segments.drop(item[1].name, inplace=True)
        # 如果首尾都是向上笔，则保留最低价的笔，删除其他笔。等同于将所有短线段合并到前后完整的线段
        elif self._is_top(first) and self._is_top(last):
            min_low_item = min(short_segments, key=lambda x: x[1]["Low"])
            for item in short_segments:
                if item is not min_low_item:
                    segments.drop(item[1].name, inplace=True)
        # 删除所有短线段。等同于将所有短线段和前后完整的线段合并成一条线段
        else:
            for item in short_segments:
                if item[1] is not first and item[1] is not last:
                    segments.drop(item[1].name, inplace=True)
            if (self._is_top(first) and first["Low"] > last["High"]
                    or self._is_bottom(first) and first["High"] < last["Low"]):
                segments.drop(first.name, inplace=True)
                segments.drop(last.name, inplace=True)
            if short_segments[-1][0] - short_segments[0][0] < 3:
                if segments.iloc[0].name == first.name:
                    segments.drop(first.name, inplace=True)
                else:
                    return [short_segments[0], short_segments[-1]]

        return []


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
    segment.generate()
