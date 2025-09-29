import pandas as pd

from chan.layer import Layer


# 缠论信号类
class Signal(Layer):

    # 生成一个时间周期的数据（捕获信号）
    def generate_interval(self, interval, data):
        # 初始化空的信号数据集
        signals = pd.DataFrame(columns=["High", "Low"])
        if len(data) == 0:
            return signals

        return signals
