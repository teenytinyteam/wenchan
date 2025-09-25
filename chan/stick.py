import pandas as pd

from chan.layer import Layer
from chan.source import Source


# 缠论K线类
class Stick(Layer):

    def __init__(self, parent: Source, auto_load=False, auto_save=True):
        super().__init__(parent, auto_load, auto_save)

    # 合并K线
    def load_interval(self, data):
        # 初始化空的K线数据集
        sticks = pd.DataFrame(columns=self.columns)

        if len(data) == 0:
            return sticks

        # 保存第一条K线
        current = self._get_item(data, 0)
        self._keep_item(sticks, current)

        # 遍历剩余K线
        index = 1
        while index < len(data):
            # 记录前一条K线
            before = current
            # 获得当前K线
            current = self._get_item(data, index).copy()
            # 根据合并方向决定合并最低价，还是最高价
            merge_column = "Low" if self._go_up(before, current) else "High"

            # 如果无法确认K线方向，则删除前一条K线，从当前K线（用于处理最初的数据）
            if not self._go_up(before, current) and not self._go_down(before, current):
                self._drop_item(sticks, before)
                self._keep_item(sticks, current)
                continue

            # 保留最后一条K线
            if index == len(data) - 1:
                self._keep_item(sticks, current)

            # 检查后续K线，直到无法合并
            while index < len(data) - 1:
                # 获得下一条K线
                after = self._get_item(data, index + 1).copy()

                # 如果当前K线包含下一条K线，则将其合并
                if self._can_merge_inside(current, after):
                    current[merge_column] = after[merge_column]
                    index += 1
                # 如果当前K线被下一条K线包含，则合并到下一条K线
                elif self._can_merge_outside(current, after):
                    after[merge_column] = current[merge_column]
                    current = after
                    index += 1
                # 如果没有包含关系，则保留当前K线，继续处理下一条K线
                else:
                    self._keep_item(sticks, current)
                    break

            index += 1

        return sticks

    # K线是否向上
    @staticmethod
    def _go_up(first, second):
        return first["High"] <= second["High"] and first["Low"] <= second["Low"]

    # K线是否向下
    @staticmethod
    def _go_down(first, second):
        return first["High"] >= second["High"] and first["Low"] >= second["Low"]

    # 当前K线是否包含下一条K线
    @staticmethod
    def _can_merge_inside(current, after):
        return current["High"] >= after["High"] and current["Low"] <= after["Low"]

    # 当前K线是否被下一条K线包含
    @staticmethod
    def _can_merge_outside(current, after):
        return current["High"] <= after["High"] and current["Low"] >= after["Low"]


if __name__ == '__main__':
    source = Source("AAPL", auto_load=False)
    stick = Stick(source, auto_load=True)
