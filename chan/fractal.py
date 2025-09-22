import os
from typing import Dict

import numpy as np
import pandas as pd

from chan.history import History
from chan.stick import Stick


class Fractal:

    def __init__(self, stick: Stick, auto_load=False, auto_save=True):
        self.stick = stick
        self.data: Dict[str, pd.DataFrame] = {}

        if auto_load:
            self.load()
            if auto_save:
                self.save()

    def load(self):
        for interval, data in self.stick.data.items():
            self.data[interval] = self._find_fractal(data)

    def _find_fractal(self, data):
        fractals = pd.DataFrame(columns=["High", "Low"])

        if len(data) == 0:
            return fractals

        for index in range(1, len(data) - 1):
            before = data.iloc[index - 1]
            current = data.iloc[index]
            after = data.iloc[index + 1]

            if self._is_top_fractal(current, before, after):
                fractals.loc[current.name] = [current["High"], np.nan]
            elif self._is_bottom_fractal(current, before, after):
                fractals.loc[current.name] = [np.nan, current["Low"]]
            else:
                fractals.loc[current.name] = [np.nan, np.nan]

        return fractals

    @staticmethod
    def _is_bottom_fractal(current, before, after):
        return current["Low"] < before["Low"] and current["Low"] < after["Low"]

    @staticmethod
    def _is_top_fractal(current, before, after):
        return current["High"] > before["High"] and current["High"] > after["High"]

    def save(self):
        folder = f'../data/{self.stick.history.symbol}'
        os.makedirs(folder, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(f'{folder}/fractal_{interval}.csv', index_label='Date')

    def get_data(self, interval):
        return self.data.get(interval)


if __name__ == '__main__':
    fractal = Fractal(Stick(History("AAPL",
                                    auto_load=True),
                            auto_load=True),
                      auto_load=True)
