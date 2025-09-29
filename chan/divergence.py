import pandas as pd

from chan.layer import Layer


# 缠论背驰类
class Divergence(Layer):

    # 生成一个时间周期的数据（判断背驰）
    def generate_interval(self, interval, data):
        # 初始化空的背驰数据集
        divergences = pd.DataFrame(columns=["High", "Low"])
        if len(data) == 0:
            return divergences

        return divergences
