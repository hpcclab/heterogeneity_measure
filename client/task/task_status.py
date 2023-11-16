"""

TODO: Add description

"""

from enum import Enum, unique
from typing import Literal


@unique
class TaskStatus(Enum):
    ARRIVING: Literal[0] = 0
    CANCELLED: Literal[1] = 1
    PENDING: Literal[2] = 2
    RUNNING: Literal[3] = 3
    COMPLETED: Literal[4] = 4
    XCOMPLETED: Literal[5] = 5
    DEFERRED: Literal[6] = 6
    DROPPED: Literal[7] = 7

    def __str__(self) -> str:
        return self.name
