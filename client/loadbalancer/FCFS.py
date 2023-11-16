"""
TODO: Add docstring
"""
import asyncio
import requests


class FCFS:
    """
    TODO: Add docstring
    """
    def __new__(cls):
        if not hasattr(cls, 'instance'):
            cls.instance = super(FCFS, cls).__new__(cls)
        return cls.instance

    def __init__(self):
        self.last_alloc_index = -1
        self.clients = {}
        self.machines = []
        self.queues = {}


    def get_client(self, task):
        available_machines_idx = []
        for i, machine in enumerate(self.machines):
            if len(self.queues[machine.name]) == 0:
                available_machines_idx.append(i)
        if len(available_machines_idx)==0:
            return None, None

        if self.last_alloc_index < max(available_machines_idx):
            assigned_machine_idx = min([x for x in available_machines_idx if x> self.last_alloc_index])
        else:
            assigned_machine_idx = min(available_machines_idx)
        client_name = self.machines[assigned_machine_idx].name
        self.queues[client_name].append(task)
        self.last_alloc_index = assigned_machine_idx
        return self.machines[assigned_machine_idx], self.clients[client_name]



