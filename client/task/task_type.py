"""

TODO: add description

"""
import os

from task.task_urgency import TaskUrgency
from utils.descriptors import TypedValueDict


class TaskType:
    """
    TODO: add description
    """
    id: int = 0
    allowed_types = [folder for folder in os.listdir('./apps')
                                if os.path.isdir(os.path.join('./apps', folder))]

    def __init__(self, name) -> None:
        if name not in TaskType.allowed_types:
            raise ValueError('Task type name does not exist in the list of apps')
        self._name: str = name
        TaskType.id += 1
        self.id = TaskType.id
        self._urgency: TaskUrgency = TaskUrgency.BESTEFFORT
        self._deadline: float = float('inf')
        self._expected_execution_times: TypedValueDict = TypedValueDict()

    @classmethod
    def get_id(cls) -> int:
        return cls.id

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name) -> None:
        if name not in TaskType.allowed_types:
            raise ValueError('Task type name does not exist in the list of apps')
        self._name = name

    @property
    def deadline(self) -> float:
        return self._deadline

    @deadline.setter
    def deadline(self, deadline) -> None:
        if not isinstance(deadline, (int, float)):
            raise TypeError('Deadline of the task type must be a'
                            'float value')
        elif deadline < 0:
            raise ValueError('Deadline of the task type cannot be'
                             'a negative value')
        self._idle_power = deadline

    @property
    def expected_execution_times(self) -> TypedValueDict:
        return self._expected_execution_times

    @expected_execution_times.setter
    def expected_execution_times(self,
                                 expected_execution_times: TypedValueDict
                                 ) -> None:
        if not isinstance(expected_execution_times, TypedValueDict):
            raise TypeError('Expected execution times of the task must be a'
                            'FloatDict value')
        self._expected_execution_times = TypedValueDict(
            expected_execution_times)
