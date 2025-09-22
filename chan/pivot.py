import os
from typing import Dict

import numpy as np
import pandas as pd

from chan.fractal import Fractal
from chan.history import History
from chan.stick import Stick
from chan.stroke import Stroke


class Pivot:

    def __init__(self, stroke: Stroke, auto_load=False, auto_save=True):
        self.stroke = stroke
        self.data: Dict[str, pd.DataFrame] = {}

        if auto_load:
            self.load()
            if auto_save:
                self.save()

    def load(self):
        for interval, data in self.stroke.data.items():
            self.data[interval] = self._find_segment(data)

    def _find_segment(self, data):
        segments = pd.DataFrame(columns=["High", "Low"])

        if len(data) == 0:
            return segments

        index = 0
        while index < len(data) - 3:
            start = data.iloc[index]
            end = None

            for step in range(3, len(data) - 1 - index, 2):
                min_high, max_low = self._get_min_high_max_low(data, index, index + step)
                if min_high < max_low:
                    step -= 2
                    break
                end = data.iloc[index + step]

            index += step

            if end is None:
                end = data.iloc[index]

            segments.loc[start.name] = start
            segments.loc[end.name] = end

        return segments

    @staticmethod
    def _get_min_high_max_low(data, begin, end):
        min_high, max_low = None, None

        for index in range(begin, end + 1):
            current = data.iloc[index]
            if not np.isnan(current["High"]):
                if min_high is None or current["High"] < min_high:
                    min_high = current["High"]
            if not np.isnan(current["Low"]):
                if max_low is None or current["Low"] > max_low:
                    max_low = current["Low"]

        return min_high, max_low

    def save(self):
        folder = f'../data/{self.stroke.fractal.stick.history.symbol}'
        os.makedirs(folder, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(f'{folder}/segment_{interval}.csv', index_label='Date')

    def get_data(self, interval):
        return self.data.get(interval)


if __name__ == '__main__':
    segment = Pivot(Stroke(Fractal(Stick(History("AAPL",
                                                   auto_load=True),
                                           auto_load=True),
                                     auto_load=True),
                             auto_load=True),
                      auto_load=True)
