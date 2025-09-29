from enum import Enum

import yfinance as yf

from chan.layer import Layer


# Yahoo财经数据不同周期可下载最大范围
class Period(Enum):
    MIN_1 = "8d"
    MIN_5 = "60d"
    MIN_30 = "60d"
    HOUR_1 = "730d"
    DAY_1 = "max"
    WEEK_1 = "max"
    MONTH_1 = "max"


# Yahoo财经数据源类
class Source(Layer):

    # 下载一个时间周期的数据
    def generate_interval(self, interval, data):
        try:
            ticker = yf.Ticker(self.symbol)
            return ticker.history(
                period=Period[interval.name].value,
                interval=interval.value,
                actions=False
            )
        except Exception as e:
            print(f"Error fetching {self.symbol} data for {interval.value}: {e}")
            return None


if __name__ == '__main__':
    source = Source("AAPL")
    source.generate()
