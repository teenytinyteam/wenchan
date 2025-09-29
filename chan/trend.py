import pandas as pd

from chan.layer import Layer


# 缠论走势类
class Trend(Layer):

    # 生成一个时间周期的数据（分辨走势）
    def generate_interval(self, interval, data):
        # 初始化空的走势数据集
        trends = pd.DataFrame(columns=["High", "Low"])
        if len(data) == 0:
            return trends

        return trends
