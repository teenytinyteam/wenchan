import os
from typing import Dict

import pandas as pd

from chan.history import History


class Stick:

    def __init__(self, history: History, auto_load=False, auto_save=True):
        self.history = history
        self.data: Dict[str, pd.DataFrame] = {}

        if auto_load:
            self.load()
            if auto_save:
                self.save()

    def load(self):
        for interval, data in self.history.data.items():
            self.data[interval] = self._merge_sticks(data)

    def _merge_sticks(self, data):
        sticks = pd.DataFrame(columns=["High", "Low"])

        if len(data) == 0:
            return sticks

        current = data.iloc[0].copy()
        sticks.loc[current.name] = current[["High", "Low"]]

        index = 1
        while index < len(data):
            before = current
            current = data.iloc[index].copy()

            up = current["High"] > before["High"] and current["Low"] > before["Low"]
            down = current["High"] < before["High"] and current["Low"] < before["Low"]

            if not up and not down:
                sticks.drop(before.name, inplace=True)
                sticks.loc[current.name] = current[["High", "Low"]]
                continue

            while index < len(data) - 1:
                after = data.iloc[index + 1].copy()

                if self._can_merge_inside(current, after):
                    if up:
                        current["Low"] = after["Low"]
                    else:
                        current["High"] = after["High"]
                    index += 1
                elif self._can_merge_outside(current, after):
                    if up:
                        after["Low"] = current["Low"]
                    else:
                        after["High"] = current["High"]
                    current = after
                    index += 1
                else:
                    sticks.loc[current.name] = current[["High", "Low"]]
                    break

            if index == len(data) - 1:
                sticks.loc[current.name] = current[["High", "Low"]]

            index += 1

        return sticks

    @staticmethod
    def _can_merge_inside(current, after):
        return current["High"] >= after["High"] and current["Low"] <= after["Low"]

    @staticmethod
    def _can_merge_outside(current, after):
        return current["High"] <= after["High"] and current["Low"] >= after["Low"]

    def save(self):
        folder = f'../data/{self.history.symbol}'
        os.makedirs(folder, exist_ok=True)
        for interval, data in self.data.items():
            if data is not None:
                data.to_csv(f'{folder}/stick_{interval}.csv', index_label='Date')

    def get_data(self, interval):
        return self.data.get(interval)


if __name__ == '__main__':
    stick = Stick(History("AAPL",
                          auto_load=True)
                  , auto_load=True)
