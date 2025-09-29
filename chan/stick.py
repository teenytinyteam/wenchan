import pandas as pd

from chan.layer import Layer
from chan.source import Source


# 缠论线类
class Stick(Layer):

    # 生成一个时间周期的数据（线的合并）
    def generate_interval(self, interval, data):
        # 初始化线数据集
        sticks = pd.DataFrame(columns=["High", "Low"])
        if len(data) < 1:
            return sticks

        # 寻找第一条走势明确的K线作为起点
        index = 0
        current = self._get_item(data, index)
        while index < len(data) - 1:
            after = self._get_item(data, index + 1)
            if self._is_go_up(current, after) or self._is_go_down(current, after):
                break
            current = after
            index += 1
        self._keep_item(sticks, current)

        # 遍历剩余K线
        index += 1
        while index < len(data):
            before = current
            current = self._get_item(data, index).copy()

            # 根据线的走势决定合并最低价，还是最高价
            merge_column = "Low" if self._is_go_up(before, current) else "High"

            # 检查后续线，直到无法合并
            while index < len(data) - 1:
                after = self._get_item(data, index + 1).copy()

                # 如果当前线包含下一条线，则将其合并
                if self._can_merge_inside(current, after):
                    current[merge_column] = after[merge_column]
                    index += 1
                # 如果当前线被下一条线包含，则合并到下一条线
                elif self._can_merge_outside(current, after):
                    after[merge_column] = current[merge_column]
                    current = after
                    index += 1
                # 如果没有包含关系，则保存当前线，继续处理下一条线
                else:
                    self._keep_item(sticks, current)
                    break

            index += 1

        self._keep_item(sticks, current)
        return sticks

    # 下一条线是否向上
    @staticmethod
    def _is_go_up(current, after):
        return current["High"] <= after["High"] and current["Low"] <= after["Low"]

    # 下一条线是否向下
    @staticmethod
    def _is_go_down(current, after):
        return current["High"] >= after["High"] and current["Low"] >= after["Low"]

    # 当前线是否包含下一条线
    @staticmethod
    def _can_merge_inside(current, after):
        return current["High"] >= after["High"] and current["Low"] <= after["Low"]

    # 当前线是否被下一条线包含
    @staticmethod
    def _can_merge_outside(current, after):
        return current["High"] <= after["High"] and current["Low"] >= after["Low"]


if __name__ == '__main__':
    source = Source("AAPL")
    source.load_from_csv()

    stick = Stick(source)
    stick.generate()
