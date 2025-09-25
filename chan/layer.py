from abc import ABC, abstractmethod

from chan.base import Base


# 缠论基础类
class Layer(Base, ABC):

    def __init__(self, parent: Base, auto_load=False, auto_save=True):
        # 底层对象
        self.parent = parent

        self.columns = ["High", "Low"]
        super().__init__(parent.symbol, auto_load, auto_save)

    # 载入数据
    def load(self):
        for interval, data in self.parent.data.items():
            self.data[interval] = self.load_interval(data)

    @abstractmethod
    def load_interval(self, data):
        pass

    # 获取数据项
    @staticmethod
    def _get_item(data, index):
        return data.iloc[index]

    # 保留数据项
    def _keep_item(self, sticks, current):
        sticks.loc[current.name] = current[self.columns]

    # 删除数据项
    @staticmethod
    def _drop_item(sticks, current):
        sticks.drop(current.name, inplace=True)
