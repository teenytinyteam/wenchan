import numpy as np
import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick


# 缠论笔类
class Stroke(Layer):

    def __init__(self, parent: Fractal, auto_load=False, auto_save=True):
        super().__init__(parent, auto_load, auto_save)

    def load_interval(self, data):
        # 初始化空的笔数据集
        strokes = pd.DataFrame(columns=self.columns)

        if len(data) == 0:
            return strokes

        # 用于存储短笔的临时列表
        short_strokes = []
        short_indexes = []
        before = None

        # 遍历分型，寻找笔
        for index in range(len(data) - 4):
            # 获得当前分型
            current = self._get_item(data, index).copy()

            # 如果当前分型和前一个分型可能构成笔（一个是顶分型，另一个时是底分型）
            if self._is_qualified_fractal(current, before):
                # 如果当前分型后面有至少3个非分型K线，则构成完整一笔，保留该分型
                if self.is_full_stroke(data, index):
                    self._keep_item(strokes, current)
                    before = current
                    # 合并之前的短笔
                    short_strokes.append(current)
                    short_indexes.append(index)
                    self._merge_short_strokes(strokes, short_strokes, short_indexes)
                    short_strokes = []
                    short_indexes = []
                # 否则，如果当前分型后续走势改变了方向，则构成短笔，暂时保留该分型
                elif self.is_short_stroke(current, data, index):
                    self._keep_item(strokes, current)
                    before = current
                    short_strokes.append(current)
                    short_indexes.append(index)

        return strokes

    # 判断是否为顶分型
    @staticmethod
    def _is_top_fractal(current):
        return not np.isnan(current["High"])

    # 判断是否为底分型
    @staticmethod
    def _is_bottom_fractal(current):
        return not np.isnan(current["Low"])

    # 判断是否为分型
    def _is_fractal(self, current):
        return self._is_top_fractal(current) or self._is_bottom_fractal(current)

    # 判断当前分型和前一个分型是否可能构成笔
    def _is_qualified_fractal(self, current, before):
        if before is None:
            return self._is_fractal(current)

        if self._is_top_fractal(before):
            return self._is_bottom_fractal(current)

        if self._is_bottom_fractal(before):
            return self._is_top_fractal(current)

        return False

    # 判断当前分型后面是否有至少3个非分型K线，可以构成完整一笔
    def is_full_stroke(self, data, index):
        if index > len(data) - 4:
            return False

        return (not self._is_fractal(data.iloc[index + 1])
                and not self._is_fractal(data.iloc[index + 2])
                and not self._is_fractal(data.iloc[index + 3]))

    # 判断当前分型后续走势是否改变了方向，或者后续是完整的一笔，则构成短笔
    def is_short_stroke(self, current, data, index):
        for i in range(len(data) - index):
            after = data.iloc[index + 1 + i]

            # 如果后续是完整的一笔，则构成短笔
            if self._is_top_fractal(current) and self._is_bottom_fractal(after):
                if self.is_full_stroke(data, index + 1 + i):
                    return True

            if self._is_bottom_fractal(current) and self._is_top_fractal(after):
                if self.is_full_stroke(data, index + 1 + i):
                    return True

            # 如果后续走势改变了方向，则构成短笔
            if self._is_top_fractal(current) and self._is_top_fractal(after):
                return current["High"] > after["High"]

            if self._is_bottom_fractal(current) and self._is_bottom_fractal(after):
                return current["Low"] < after["Low"]

        return False

    # 合并短笔
    def _merge_short_strokes(self, strokes, short_strokes, short_indexes):
        if len(short_strokes) < 2:
            return

        # 取出首尾两个短笔
        first = short_strokes[0]
        last = short_strokes[-1]

        # 如果首尾都是顶分型，则保留最高价的分型，删除其他分型。等同于将所有短笔合并到前后完整的笔
        if self._is_top_fractal(first) and self._is_top_fractal(last):
            max_high_item = max(short_strokes, key=lambda x: x["High"])
            for item in short_strokes:
                if item is not max_high_item:
                    strokes.drop(item.name, inplace=True)
        # 如果首尾都是底分型，则保留最低价的分型，删除其他分型。等同于将所有短笔合并到前后完整的笔
        elif self._is_bottom_fractal(first) and self._is_bottom_fractal(last):
            min_low_item = min(short_strokes, key=lambda x: x["Low"])
            for item in short_strokes:
                if item is not min_low_item:
                    strokes.drop(item.name, inplace=True)
        else:
            # 删除所有短笔。等同于将所有短笔和前后完整的笔合并成一笔
            if short_indexes[-1] - short_indexes[0] >= 4:
                for item in short_strokes:
                    if item is not first and item is not last:
                        strokes.drop(item.name, inplace=True)
            else:
                for item in short_strokes:
                    strokes.drop(item.name, inplace=True)


if __name__ == '__main__':
    source = Source("AAPL", auto_load=False)
    stick = Stick(source, auto_load=False)
    fractal = Fractal(stick, auto_load=False)
    stroke = Stroke(fractal, auto_load=True)
