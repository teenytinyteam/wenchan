import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer, Interval
from chan.pivot import Pivot
from chan.segment import Segment_1
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke_1


# 缠论走势类
class Trend(Layer):

    # 生成数据
    def generate(self, auto_save=True):
        for interval in Interval:
            pivot_data = self.parent.data[interval.value]
            pivot_data.columns = ['Pivot_High', 'Pivot_Low']
            segment_data = self.parent.parent.data[interval.value]
            segment_data.columns = ['Segment_High', 'Segment_Low']
            data = segment_data.join(pivot_data, how='left')
            self.data[interval.value] = self.generate_interval(interval, data)
        if auto_save:
            self.save()

    # 生成一个时间周期的数据（分辨走势）
    def generate_interval(self, interval, data):
        # 初始化空的走势数据集
        trends = pd.DataFrame(columns=["High", "Low"])
        if len(data) == 0:
            return trends

        return trends


if __name__ == '__main__':
    source = Source("AAPL")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.load_from_csv()

    stroke = Stroke_1(fractal)
    stroke.load_from_csv()

    segment = Segment_1(stroke)
    segment.load_from_csv()

    pivot = Pivot(segment)
    pivot.load_from_csv()

    trend = Trend(segment)
    trend.generate()
