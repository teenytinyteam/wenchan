import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick


# 缠论笔类
class Stroke(Layer):

    def __init__(self, parent):
        super().__init__(parent)
        self.length = 4

    # 生成一个时间周期的数据（划分笔）
    def generate_interval(self, interval, data):
        # 初始化空的笔数据集
        strokes = pd.DataFrame(columns=["High", "Low"])
        if len(data) <= self.length:
            return strokes

        # 等待处理的分型
        fractals = []

        # 遍历所有分型
        for index in range(len(data)):
            item = self._get_item(data, index)
            if self._is_fractal(item):
                fractals.append({"index": index, "item": item})

                count = len(fractals)
                if count == 2:
                    fractals = self._two_fractals(strokes, fractals)
                elif count == 3:
                    fractals = self._three_fractals(strokes, fractals)
                elif count == 4:
                    fractals = self._four_fractals(strokes, fractals)
                elif count == 5:
                    fractals = self._five_fractals(strokes, fractals)
                elif count == 6:
                    fractals = self._six_fractals(strokes, fractals)

        return strokes

    # 判断是否为分型
    def _is_fractal(self, current):
        return self._is_top(current) or self._is_bottom(current)

    # 如果两个分型是否可以组成完整的笔
    def _two_fractals(self, strokes, fractals):
        current = fractals[0]
        first = fractals[1]

        if first["index"] - current["index"] >= self.length:
            self._keep_item(strokes, current["item"])
            return [first]
        return fractals

    # 如果第三个分型延续之前的趋势，则和前笔合并
    def _three_fractals(self, strokes, fractals):
        current = fractals[0]
        second = fractals[2]

        if (self._is_top(current["item"]) and second["item"]["High"] >= current["item"]["High"]
                or self._is_bottom(current["item"]) and second["item"]["Low"] <= current["item"]["Low"]):
            return [second]
        return fractals

    # 判断四个分型是否可以组成一笔
    def _four_fractals(self, strokes, fractals):
        current = fractals[0]
        third = fractals[3]

        if third["index"] - current["index"] >= self.length:
            self._keep_item(strokes, current["item"])
            return [third]
        return fractals

    # 如果第五个分型延续之前的趋势，则和前笔合并
    def _five_fractals(self, strokes, fractals):
        current = fractals[0]
        fourth = fractals[4]

        if (self._is_top(current["item"]) and fourth["item"]["High"] >= current["item"]["High"]
                or self._is_bottom(current["item"]) and fourth["item"]["Low"] <= current["item"]["Low"]):
            return [fourth]
        return fractals

    # 六个分型组成一笔
    def _six_fractals(self, strokes, fractals):
        current = fractals[0]
        fifth = fractals[5]

        self._keep_item(strokes, current["item"])
        return [fifth]


if __name__ == '__main__':
    source = Source("002594.SZ")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.load_from_csv()

    stroke = Stroke(fractal)
    stroke.generate()
