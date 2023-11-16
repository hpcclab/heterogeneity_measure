"""
TODO: Add docstring
"""
from machine.machine_type import MachineType


class Machine:

    id: int = 0
    component = 'Machine'

    def __init__(self, instance_id: str, name: str, machine_type: MachineType, instance_ip: str):
        Machine.id += 1
        self.id: int = Machine.id
        self.name = name
        self.machine_type: MachineType = machine_type
        self.instance_id: str = instance_id
        self.instance_ip: str = instance_ip
