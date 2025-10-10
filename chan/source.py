from enum import Enum

import pandas as pd
import yfinance as yf

from chan.layer import Layer, Interval


# Yahoo财经数据不同周期可下载最大范围
class Period(Enum):
    MIN_1 = "5d"
    MIN_5 = "30d"
    MIN_30 = "60d"
    HOUR_1 = "1y"
    DAY_1 = "10y"
    WEEK_1 = "max"
    MONTH_1 = "max"


# Yahoo财经数据源类
class Source(Layer):

    # 生成数据
    def generate(self, auto_save=True):
        for interval in Interval:
            self.data[interval.value] = self.generate_interval(interval, None)
        if auto_save:
            self.save()

    # 下载一个时间周期的数据
    def generate_interval(self, interval, data):
        try:
            ticker = yf.Ticker(self.symbol)
            df = ticker.history(
                period=Period[interval.name].value,
                interval=interval.value,
                actions=False
            )

            if df is not None and not df.empty:
                if self.symbol.endswith(".SZ") or self.symbol.endswith(".SS"):
                    if interval in [Interval.MIN_1, Interval.MIN_5, Interval.MIN_30, Interval.HOUR_1]:
                        df = self.filter_cn_a_share_trading_time(df)
                df = self.calculate_macd(df)
            return df

        except Exception as e:
            print(f"Error fetching {self.symbol} data for {interval.value}: {e}")
            return None

    @staticmethod
    def filter_cn_a_share_trading_time(df):
        if df.index.tz is None:
            df.index = df.index.tz_localize("UTC")
        df = df.tz_convert("Asia/Shanghai")

        time_mask = (
                ((df.index.time >= pd.Timestamp("09:30").time())
                 & (df.index.time <= pd.Timestamp("11:30").time()))
                | ((df.index.time >= pd.Timestamp("13:00").time())
                   & (df.index.time <= pd.Timestamp("15:00").time())))
        return df[time_mask].copy()

    @staticmethod
    def calculate_macd(df, fast=12, slow=26, signal=9):
        ema_fast = df['Close'].ewm(span=fast, adjust=False).mean()
        ema_slow = df['Close'].ewm(span=slow, adjust=False).mean()

        df['MACD'] = ema_fast - ema_slow
        df['Signal'] = df['MACD'].ewm(span=signal, adjust=False).mean()
        df['Histogram'] = df['MACD'] - df['Signal']
        return df


if __name__ == '__main__':
    source = Source("SQQQ")
    source.generate()
