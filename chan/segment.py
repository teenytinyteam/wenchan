import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick
from chan.stroke import Stroke


# 缠论线段类
class Segment(Layer):

    def __init__(self, parent):
        super().__init__(parent)
        self.length = 3

    # 生成一个时间周期的数据（划分线段）
    def generate_interval(self, interval, data):
        # 初始化空的线段数据集
        segments = pd.DataFrame(columns=["High", "Low"])
        if len(data) <= self.length:
            return segments

        # 等待处理的笔
        strokes = []

        # 遍历所有笔
        for index in range(len(data)):
            current = self._get_item(data, index)
            strokes.append({"index": index, "item": current})

            count = len(strokes)
            if count == 3:
                strokes = self._three_strokes(segments, strokes)
            elif count == 4:
                strokes = self._four_strokes(segments, strokes)
            elif count == 5:
                strokes = self._five_strokes(segments, strokes)
            elif count >= 6 and count % 2 == 0:
                strokes = self._six_strokes(segments, strokes)
            elif count >= 7 and count % 2 != 0:
                strokes = self._seven_strokes(segments, strokes)

        return segments

    # 如果第二笔延续之前的趋势，则合并到前线段
    def _three_strokes(self, segments, strokes):
        current = strokes[0]
        second = strokes[2]

        if (self._is_top(current["item"]) and second["item"]["High"] >= current["item"]["High"]
                or self._is_bottom(current["item"]) and second["item"]["Low"] <= current["item"]["Low"]):
            return [second]
        return strokes

    # 判断三笔是否组成完整的线段
    def _four_strokes(self, segments, strokes):
        current = strokes[0]
        first = strokes[1]
        third = strokes[3]

        if (self._is_top(current["item"]) and third["item"]["Low"] <= first["item"]["Low"]
                or self._is_bottom(current["item"]) and third["item"]["High"] >= first["item"]["High"]):
            self._keep_item(segments, current["item"])
            return [third]
        return strokes

    # 如果第四笔延续之前的趋势，则合并到前线段
    def _five_strokes(self, segments, strokes):
        current = strokes[0]
        fourth = strokes[4]

        if (self._is_top(current["item"]) and fourth["item"]["High"] >= current["item"]["High"]
                or self._is_bottom(current["item"]) and fourth["item"]["Low"] <= current["item"]["Low"]):
            return [fourth]
        return strokes

    # 判断五笔以上，单数笔是否可以组成线段
    def _six_strokes(self, segments, strokes):
        current = strokes[0]
        third = strokes[-3]
        fifth = strokes[-1]

        if (self._is_top(current["item"]) and fifth["item"]["Low"] <= third["item"]["Low"]
                or self._is_bottom(current["item"]) and fifth["item"]["High"] >= third["item"]["High"]):
            self._keep_item(segments, current["item"])
            return [fifth]
        return strokes

    # 判断六笔以上，双数笔是否可以分割成两个线段
    def _seven_strokes(self, segments, strokes):
        current = strokes[0]
        fourth = strokes[-3]
        sixth = strokes[-1]

        if (self._is_top(current["item"]) and sixth["item"]["High"] >= fourth["item"]["High"]
                or self._is_bottom(current["item"]) and sixth["item"]["Low"] <= fourth["item"]["Low"]):
            self._keep_item(segments, current["item"])
            if self._is_top(current["item"]):
                self._keep_item(segments, self._middle_lowest(strokes)["item"])
            else:
                self._keep_item(segments, self._middle_highest(strokes)["item"])
            return [sixth]
        return strokes

    # 找到中间最低分型
    @staticmethod
    def _middle_lowest(strokes):
        lowest = None
        for index in range(3, len(strokes) - 3):
            low = strokes[index]
            if lowest is None or low["item"]["Low"] < lowest["item"]["Low"]:
                lowest = low
        return lowest

    # 找斗中间最高分型
    @staticmethod
    def _middle_highest(strokes):
        highest = None
        for index in range(3, len(strokes) - 3):
            high = strokes[index]
            if highest is None or high["item"]["High"] > highest["item"]["High"]:
                highest = high
        return highest


if __name__ == '__main__':
    source = Source("SQQQ")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.load_from_csv()

    stroke = Stroke(fractal)
    stroke.load_from_csv()

    segment = Segment(stroke)
    segment.generate()
