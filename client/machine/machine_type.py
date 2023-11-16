"""
TODO: Add docstring
"""
import pandas as pd


class MachineType:
    """
    TODO: Add docstring
    """

    id: int = 0
    allowed_instance_types = pd.read_csv("aws_ec2_instance_types.csv")

    def __init__(self, name):
        aws_ec2_instance_type: dict = self.allowed_instance_types.loc[
                                            self.allowed_instance_types['InstanceType'] == name, :]
        if aws_ec2_instance_type.shape[0] == 0:
            raise ValueError(f"Machine type {name} not found in AWS EC2 instance types")
        MachineType.id += 1
        self.id: int = MachineType.id
        self.name: str = name
        self.vCPU: int = aws_ec2_instance_type['vCPU'].values[0]
        self.memory: int = aws_ec2_instance_type['Memory'].values[0]
        self.gpu_type: str = aws_ec2_instance_type['GPUType'].values[0]
        if self.gpu_type:
            self.gpu_type: str = aws_ec2_instance_type['GPUType'].values[0]
            self.gpu_count: int = aws_ec2_instance_type['GPUCount'].values[0]
            self.gpu_memory: int = aws_ec2_instance_type['GPUMemory'].values[0]
        else:
            self.gpu_type = None
            self.gpu_count: int = 0
            self.gpu_memory: int = 0

    def __str__(self):
        return self.name
