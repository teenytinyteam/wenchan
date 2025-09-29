import pandas as pd

from chan.fractal import Fractal
from chan.layer import Layer
from chan.source import Source
from chan.stick import Stick


# 缠论笔类
class Stroke(Layer):

    # 生成一个时间周期的数据（划分笔）
    def generate_interval(self, interval, data):
        # 初始化空的笔数据集
        strokes = pd.DataFrame(columns=["High", "Low"])
        if len(data) == 0:
            return strokes

        # 用于存储短笔的临时列表
        short_strokes = []

        # 遍历分型，寻找笔
        before = None
        for index in range(len(data) - 4):
            current = self._get_item(data, index).copy()

            # 如果当前分型和前一个分型可能构成笔（一个是顶分型，另一个时是底分型）
            if self._is_qualified_fractal(current, before):
                # 如果当前分型后面有至少3个非分型线，则构成完整一笔
                full_stroke = self._is_full_stroke(data, index)
                # 否则，如果当前分型后续走势改变了方向，则构成短笔
                short_stroke = self._is_short_stroke(current, data, index)

                # 保存完整笔和短笔
                if full_stroke or short_stroke:
                    self._keep_item(strokes, current)
                    before = current
                    short_strokes.append([index, current])

                # 合并之前的短笔
                if full_stroke:
                    short_strokes = self._merge_short_strokes(strokes, short_strokes)

        return strokes

    # 判断是否为分型
    def _is_fractal(self, current):
        return self._is_top(current) or self._is_bottom(current)

    # 判断当前分型和前一个分型是否可能构成笔
    def _is_qualified_fractal(self, current, before):
        if before is None:
            return self._is_fractal(current)

        if self._is_top(before):
            return self._is_bottom(current)

        if self._is_bottom(before):
            return self._is_top(current)

        return False

    # 判断当前分型后面是否有至少3个非分型线，可以构成完整一笔
    def _is_full_stroke(self, data, index):
        if index > len(data) - 4:
            return False

        first = data.iloc[index + 1]
        second = data.iloc[index + 2]
        third = data.iloc[index + 3]
        return not self._is_fractal(first) and not self._is_fractal(second) and not self._is_fractal(third)

    # 判断当前分型后续走势是否改变了方向，或者后续是完整的一笔，则构成短笔
    def _is_short_stroke(self, current, data, index):
        for i in range(len(data) - index - 1):
            after = data.iloc[index + i + 1]

            # 如果后续是完整的一笔，则构成短笔
            if self._is_top(current) and self._is_bottom(after):
                if self._is_full_stroke(data, index + i + 1):
                    return True
            if self._is_bottom(current) and self._is_top(after):
                if self._is_full_stroke(data, index + i + 1):
                    return True

            # 如果后续走势改变了方向，则构成短笔
            if self._is_top(current) and self._is_top(after):
                return current["High"] > after["High"]
            if self._is_bottom(current) and self._is_bottom(after):
                return current["Low"] < after["Low"]

        return False

    # 合并短笔
    def _merge_short_strokes(self, strokes, short_strokes):
        if len(short_strokes) < 2:
            return []

        # 取出首尾两个短笔
        first = short_strokes[0][1]
        last = short_strokes[-1][1]

        # 如果首尾都是顶分型，则保留最高价的分型，删除其他分型。等同于将所有短笔合并到前后完整的笔
        if self._is_top(first) and self._is_top(last):
            max_high_item = max(short_strokes, key=lambda x: x[1]["High"])
            for item in short_strokes:
                if item is not max_high_item:
                    strokes.drop(item[1].name, inplace=True)
        # 如果首尾都是底分型，则保留最低价的分型，删除其他分型。等同于将所有短笔合并到前后完整的笔
        elif self._is_bottom(first) and self._is_bottom(last):
            min_low_item = min(short_strokes, key=lambda x: x[1]["Low"])
            for item in short_strokes:
                if item is not min_low_item:
                    strokes.drop(item[1].name, inplace=True)
        # 删除所有短笔。等同于将所有短笔和前后完整的笔合并成一笔
        else:
            for item in short_strokes:
                if item[1] is not first and item[1] is not last:
                    strokes.drop(item[1].name, inplace=True)
            if (self._is_top(first) and first["High"] < last["Low"]
                    or self._is_bottom(first) and first["Low"] > last["High"]):
                strokes.drop(first.name, inplace=True)
                strokes.drop(last.name, inplace=True)
            if short_strokes[-1][0] - short_strokes[0][0] < 5:
                if strokes.iloc[0].name == first.name:
                    strokes.drop(first.name, inplace=True)
                else:
                    return [short_strokes[0], short_strokes[-1]]

        return []


if __name__ == '__main__':
    source = Source("AAPL")
    source.load_from_csv()

    stick = Stick(source)
    stick.load_from_csv()

    fractal = Fractal(stick)
    fractal.load_from_csv()

    stroke = Stroke(fractal)
    stroke.generate()
