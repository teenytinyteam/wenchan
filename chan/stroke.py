import os
from typing import Dict

import numpy as np
import pandas as pd

from chan.fractal import Fractal
from chan.history import History
from chan.stick import Stick


class Stroke:

    def __init__(self, fractal: Fractal, auto_load=False, auto_save=True):
        self.fractal = fractal
        self.data: Dict[str, pd.DataFrame] = {}

        if auto_load:
            self.load()
            if auto_save:
                self.save()

    def load(self):
        for interval, data in self.fractal.data.items():
            self.data[interval] = self._find_stroke(data)

    def _find_stroke(self, data):
        strokes = pd.DataFrame(columns=["High", "Low"])

        if len(data) == 0:
            return strokes

        top = False
        bottom = False

        for index in range(len(data) - 4):
            if self._is_qualified_fractal(data, index):
                current = data.iloc[index]
                if ((top and self._is_bottom_fractal(current))
                        or (bottom and self._is_top_fractal(current))
                        or (not top and not bottom)):
                    strokes.loc[current.name] = current
                    top = self._is_top_fractal(current)
                    bottom = self._is_bottom_fractal(current)

        return strokes

    @staticmethod
    def _is_top_fractal(current):
        return not np.isnan(current["High"])

    @staticmethod
    def _is_bottom_fractal(current):
        return not np.isnan(current["Low"])

    def _is_fractal(self, current):
        return self._is_top_fractal(current) or self._is_bottom_fractal(current)

    def _is_qualified_fractal(self, data, index):
        current = data.iloc[index]
        if not self._is_fractal(current):
            return False

        if (not self._is_fractal(data.iloc[index + 1])
                and not self._is_fractal(data.iloc[index + 2])
                and not self._is_fractal(data.iloc[index + 3])):
            return True

        if self._is_top_fractal(current):
            for i in range(1, len(data) - index - 1):
                after = data.iloc[index + i]
                if self._is_top_fractal(after):
                    return after["High"] < current["High"]

        if self._is_bottom_fractal(current):
            for i in range(1, len(data) - index - 1):
                after = data.iloc[index + i]
                if self._is_bottom_fractal(after):
                    return after["Low"] > current["Low"]

        return False

    def save(self):
        folder = f'../data/{self.fractal.stick.history.symbol}'
        os.makedirs(folder, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(f'{folder}/stroke_{interval}.csv', index_label='Date')

    def get_data(self, interval):
        return self.data.get(interval)


if __name__ == '__main__':
    stroke = Stroke(Fractal(Stick(History("AAPL",
                                          auto_load=True),
                                  auto_load=True),
                            auto_load=True),
                    auto_load=True)
