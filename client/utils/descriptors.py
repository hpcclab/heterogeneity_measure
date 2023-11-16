"""

TODO: add description

"""
from __future__ import annotations
from queue import Queue

from utils.helper import is_valid_instance


class TypedList(list):
    def __init__(self, type=(int, float), values=None):
        self.type = type
        if values is None:
            values = []
        for value in values:
            if not isinstance(value, self.type):
                raise TypeError(
                    f"All values of TypedList must be {self.type} type")
        super().__init__(values)

    def append(self, value):
        if not isinstance(value, self.type):
            raise TypeError(
                f"All values of TypedList must be {self.type} type")
        super().append(value)

    def extend(self, values):
        for value in values:
            if not isinstance(value, self.type):
                raise TypeError(
                    f"All values of TypedList must be {self.type} type")
        super().extend(values)

    def insert(self, index, value):
        if not isinstance(value, self.type):
            raise TypeError(
                f"All values of TypedList must be {self.type} type")
        super().insert(index, value)

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __setitem__(self, index, value):
        if not isinstance(value, self.type):
            raise TypeError(
                f"All values of TypedList must be {self.type} type")
        super().__setitem__(index, value)

    def __repr__(self):
        return super().__repr__()


class TypedValueDict(dict):
    def __init__(self, items=None, value_type=(float, int)):
        self.value_type = value_type
        if items:
            for _, value in items.items():
                if not isinstance(value, value_type):
                    raise TypeError(f'The value must be {self.value_type}')
            super().__init__(items)

    def __setitem__(self, key, value):
        if not isinstance(value, self.value_type):
            raise TypeError(f'The value must be {self.value_type}')
        elif (not isinstance(value, TypedList) and value < 0):
            raise ValueError('The value must be positive')
        super().__setitem__(key, value)


class QTask(Queue):

    def __init__(self, maxsize=0):
        super().__init__(maxsize)

    def put(self, item):
        if not is_valid_instance(item, 'Task'):
            raise TypeError("The item must be of type Task")
        super().put(item)

    def __repr__(self):
        return super().__repr__()
