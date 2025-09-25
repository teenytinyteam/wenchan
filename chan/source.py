from enum import Enum

import yfinance as yf

from chan.base import Base, Interval


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
class Source(Base):

    # 下载数据
    def load(self):
        for interval in Interval:
            self._load_from_yahoo(interval)

    # 从Yahoo财经下载数据
    def _load_from_yahoo(self, interval):
        try:
            ticker = yf.Ticker(self.symbol)
            data = ticker.history(
                period=Period[interval.name].value,
                interval=interval.value,
                actions=False
            )
            self.data[interval.value] = data
            return data

        except Exception as e:
            print(f"Error fetching {self.symbol} data for {interval.value}: {e}")
            return None


if __name__ == '__main__':
    source = Source("AAPL", auto_load=True)
