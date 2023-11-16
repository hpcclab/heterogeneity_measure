"""
TODO: Add description
"""
import pandas as pd
import tritonclient.http as httpclient


class Run:
    """
    TODO: Add description
    """

    def __init__(self, path_to_workload, path_to_instances_info='triton_instances_info.csv'):
        self.path_to_instances_info = path_to_instances_info
        self.instances = pd.read_csv(path_to_instances_info)
        self.clients = self.create_triton_clients(self.instances)
        self.workload = self.read_workload(path_to_workload)

    def read_workload(self, workload_file):
        workload = pd.read_csv(workload_file, usecols=['task_type', 'arrival_time'])
        workload = workload.sort_values(by=['arrival_time'])
        workload = workload.reset_index(drop=True)
        return workload

    def create_triton_clients(self, instances):
        clients = []
        for _, instance in instances.iterrows():
            instance_ip = instance['PublicIpAddress']
            client = httpclient.InferenceServerClient(url=f"{instance_ip}:8000")
            clients.append(client)
        return clients

    def update_instances(self):
        self.instances = pd.read_csv(self.path_to_instances_info)
        self.clients = self.create_triton_clients(self.instances)

    def remove_instance(self, instance_id):
        self.instances = self.instances.loc[self.instances['Instance ID'] != instance_id, :]
        self.clients = self.create_triton_clients(self.instances)


