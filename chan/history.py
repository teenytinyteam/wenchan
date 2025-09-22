import os
from enum import Enum
from typing import Dict

import pandas as pd
import yfinance as yf


class Period(Enum):
    DAYS_8 = "8d"
    DAYS_60 = "60d"
    DAYS_730 = "730d"
    MAX = "max"


class Interval(Enum):
    # MIN_1 = ("1m", Period.DAYS_8)
    # MIN_5 = ("5m", Period.DAYS_60)
    # MIN_30 = ("30m", Period.DAYS_60)
    # HOUR_1 = ("1h", Period.DAYS_730)
    DAY_1 = ("1d", Period.MAX)
    # WEEK_1 = ("1wk", Period.MAX)
    # MONTH_1 = ("1mo", Period.MAX)


class History:

    def __init__(self, symbol, auto_load=False, auto_save=True):
        self.symbol = symbol
        self.data: Dict[str, pd.DataFrame] = {}
        self._ticker = yf.Ticker(symbol)

        if auto_load:
            self.load()
            if auto_save:
                self.save()

    def load(self):
        for interval in Interval:
            self._load_from_yahoo(interval)

    def _load_from_yahoo(self, interval: Interval):
        try:
            data = self._ticker.history(
                period=interval.value[1].value,
                interval=interval.value[0],
                actions=False
            )
            self.data[interval.value[0]] = data
            return data

        except Exception as e:
            print(f"Error fetching {self.symbol} data for {interval.value[0]}: {e}")
            return None

    def save(self):
        folder = f'../data/{self.symbol}'
        os.makedirs(folder, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(f'{folder}/history_{interval}.csv')

    def get_data(self, interval):
        return self.data.get(interval)


if __name__ == '__main__':
    history = History("AAPL",
                      auto_load=True)
