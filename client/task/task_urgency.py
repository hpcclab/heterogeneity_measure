"""

TODO: Add description

"""

from enum import Enum, unique
from typing import Literal


@unique
class TaskUrgency(Enum):
    BESTEFFORT: Literal[0] = 0
    URGENT: Literal[1] = 1

    def __str__(self) -> str:
        return self.name
