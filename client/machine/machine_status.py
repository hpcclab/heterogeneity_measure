"""

TODO: Add description

"""

from enum import Enum, unique
from typing import Literal


@unique
class MachineStatus(Enum):
    TERMINATED: Literal[0] = 0
    RUNNING: Literal[1] = 1
    PENDING: Literal[2] = 2
    STOPPED: Literal[3] = 3
    STOPPING: Literal[4] = 4
    SHUTTING_DOWN: Literal[5] = 5

    def __str__(self) -> str:
        return self.name
