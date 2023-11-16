"""

TODO: add description

"""
from __future__ import annotations
import os

from task.task_status import TaskStatus
from task.task_type import TaskType


class Task:
    """
    TODO: add description
    """
    component = 'Task'
    id: int = 0

    def __init__(self, task_type: TaskType, arrival_time: float, metadata: str) -> None:
        Task.id += 1
        self.id = Task.id
        self._type: TaskType = task_type
        self._status: TaskStatus = TaskStatus.ARRIVING
        self._deferred_count: int = 0
        self._arrival_time: float = arrival_time
        self._preprocessing_time: float = 0.0
        self._execution_time: float = float('inf')
        self._completion_time: float = float('inf')
        self._makespan: float = float('inf')
        self._metadata: str = metadata
        self._data = None
        self._assigned_machine = None
        self._energy_usuage: float = 0.0
        self._wastaed_energy: bool = False
        self.deadline: float = (self.arrival_time +
                                self._type.deadline)

    def __repr__(self) -> str:
        return f'{self._type.name}-{self.id}'

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data):
        self._data = data

    @property
    def type(self) -> TaskType:
        return self._type

    @type.setter
    def type(self, task_type: TaskType) -> None:
        if not isinstance(task_type, TaskType):
            raise TypeError('Type of the task must be a'
                            'TaskType value')
        self._type = task_type

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, status: TaskStatus) -> None:
        if not isinstance(status, TaskStatus):
            raise TypeError('Status of the task must be a'
                            'TaskStatus value')
        self._status = status

    @property
    def deferred_count(self) -> int:
        return self._deferred_count

    @deferred_count.setter
    def deferred_count(self, deferred_count) -> None:
        if not isinstance(deferred_count, int):
            raise TypeError('Deferred count of the task must be an'
                            'integer value')
        elif deferred_count < self._deferred_count:
            raise ValueError('Deferred count of the task cannot be'
                             'set to a value less than the current value')
        self._deferred_count = deferred_count

    @property
    def metadata(self) -> str:
        return self._metadata

    @metadata.setter
    def metadata(self, metadata: str) -> None:
        if not os.path.isfile(metadata):
            raise FileNotFoundError('Metadata file of the task does not exist')
        self._metadata = metadata

    @property
    def arrival_time(self) -> float:
        return self._arrival_time

    @arrival_time.setter
    def arrival_time(self, arrival_time: float) -> None:
        if not isinstance(arrival_time, (float, int)):
            raise TypeError('Arrival time of the task must be a'
                            'float value')
        self._arrival_time = arrival_time

    @property
    def execution_time(self) -> float:
        return self._execution_time

    @execution_time.setter
    def execution_time(self, execution_time: float) -> None:
        if not isinstance(execution_time, (float, int)):
            raise TypeError('Execution times of the task must be a'
                            'float value')
        self._execution_time = execution_time

    @property
    def makespan(self) -> float:
        return self._makespan

    @makespan.setter
    def makespan(self, makespan: float) -> None:
        if not isinstance(makespan, (float, int)):
            raise TypeError('Makespan of the task must be a'
                            'float value')
        self._makespan = makespan

    @property
    def preprocessing_time(self) -> float:
        return self._preprocessing_time

    @preprocessing_time.setter
    def preprocessing_time(self, preprocessing_time: float) -> None:
        if not isinstance(preprocessing_time, (float, int)):
            raise TypeError('Preprocessing times of the task must be a'
                            'float value')
        self._preprocessing_time = preprocessing_time

    @property
    def completion_time(self) -> float:
        return self._completion_time

    @completion_time.setter
    def completion_time(self, completion_time: float) -> None:
        if not isinstance(completion_time, (float, int)):
            raise TypeError('Completion time of the task must be a'
                            'float value')
        self._completion_time = completion_time

    @property
    def assigned_machine(self) -> 'Machine':  # noqa F821 #pyright: ignore
        return self._assigned_machine

    @assigned_machine.setter
    def assigned_machine(self, assigned_machine: 'Machine') -> None:  # noqa F821 # pyright: ignore
        if not hasattr(assigned_machine, 'component'):
            raise AttributeError('Assigned machine must have a component'
                                 'attribute')
        elif assigned_machine.component != 'Machine':
            raise TypeError('Assigned machine type is NOT a'
                            'Machine')
        self._assigned_machine = assigned_machine

    @property
    def energy_usuage(self) -> float:
        return self._energy_usuage

    @energy_usuage.setter
    def energy_usuage(self, energy_usuage: float) -> None:
        if not isinstance(energy_usuage, float):
            raise TypeError('Energy usuage of the task must be a'
                            'float value')
        elif energy_usuage < 0:
            raise ValueError('Energy usuage of the task cannot be'
                             'a negative value')
        self._energy_usuage = energy_usuage

    @property
    def wastaed_energy(self) -> bool:
        return self._wastaed_energy

    @wastaed_energy.setter
    def wastaed_energy(self, wastaed_energy: bool) -> None:
        if not isinstance(wastaed_energy, bool):
            raise TypeError('Wastaed energy of the task must be a'
                            'bool value')
        self._wastaed_energy = wastaed_energy

    def __str__(self) -> str:
        return f'{self._type.name}-{self.id}'
