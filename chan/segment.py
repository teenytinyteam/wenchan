import os
from typing import Dict

import numpy as np
import pandas as pd

from chan.fractal import Fractal
from chan.history import History
from chan.stick import Stick
from chan.stroke import Stroke


class Segment:

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

            step = 0
            for i in range(0, len(data) - 3 - index, 2):
                higher = self._is_up_and_higher(data, index + i)
                lower = self._is_down_and_lower(data, index + i)
                if not higher and not lower:
                    step = i + 1
                    break
                step = i + 3

            index += step
            end = data.iloc[index]

            segments.loc[start.name] = start
            segments.loc[end.name] = end

        return segments

    @staticmethod
    def _is_up_and_higher(data, index):
        first = data.iloc[index + 1]
        second = data.iloc[index + 3]
        if not np.isnan(first["High"]) and not np.isnan(second["High"]):
            return second["High"] >= first["High"]
        return False

    @staticmethod
    def _is_down_and_lower(data, index):
        first = data.iloc[index + 1]
        second = data.iloc[index + 3]
        if not np.isnan(first["Low"]) and not np.isnan(second["Low"]):
            return second["Low"] <= first["Low"]
        return False

    def save(self):
        folder = f'../data/{self.stroke.fractal.stick.history.symbol}'
        os.makedirs(folder, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(f'{folder}/segment_{interval}.csv', index_label='Date')

    def get_data(self, interval):
        return self.data.get(interval)


if __name__ == '__main__':
    segment = Segment(Stroke(Fractal(Stick(History("AAPL",
                                                   auto_load=True),
                                           auto_load=True),
                                     auto_load=True),
                             auto_load=True),
                      auto_load=True)
