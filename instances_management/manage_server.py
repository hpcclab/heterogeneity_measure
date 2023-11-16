"""

"""
import subprocess
import time

from manage_instances import (start_instance, stop_instance, terminate_instance,
                              existing_instances, instance_state,
                              instance_gpus)
from manage_info import (update_info, remove_info, send_info)
from manage_triton import (start_tritonserver, kill_tritonserver,
                           send_model_repository, send_prometheus_source)
from manage_prometheus import start_prometheus, kill_prometheus
from colors import colors


def filter_instances(filters):
    """
    Filter instances based on filters
    """
    instances = existing_instances(tag_prefix="triton")
    if filters['all']:
        return instances
    filtered_instances = []
    filter_type = [key for key, value in filters.items() if value not in [None, False, True]]
    if len(filter_type) > 0:
        filter_type = filter_type[0]
    else:
        return instances
    for instance in instances:
        if filter_type == 'InstanceName':
            instance_name = instance.get('Tags')[0].get('Value')
            if instance_name in filters[filter_type]:
                filtered_instances.append(instance)
        elif filter_type == 'InstanceType':
            instance_type = instance.get('InstanceType')
            if instance_type in filters[filter_type]:
                filtered_instances.append(instance)
    return filtered_instances


def check_directory(instance_public_ip, private_key_path, directory):
    """
    Check if directory exists on instance
    """
    cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {private_key_path}  ubuntu@{instance_public_ip} '
    cmd += 'ls /home/ubuntu'
    is_existing = False
    p = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if p.returncode == 0:
        directories = p.stdout.strip().split('\n')
        if directory in directories:
            is_existing = True
        return is_existing
    else:
        print(f"Error:{p.stderr}")
        return None


def start_server(filtered_instances, triton_instances_info,
                 private_key_path="PATH_TO_AWS_KEY",
                 aws_region="us-east-2"):
    """
    Start the instances, tritonserver, and prometheus on the instances
    """
    for instance in filtered_instances:
        instance = start_instance(aws_region, instance["InstanceId"])[0]
        instance_public_ip = instance.get("PublicIpAddress", None)
        status = instance_state(instance["InstanceId"])
        if status != "terminated":
            triton_instances_info = update_info("triton_instances_info.csv",
                                                triton_instances_info, instance)
        is_tritonserver_existing = check_directory(instance_public_ip, private_key_path, "triton")
        is_prometheus_existing = check_directory(instance_public_ip,
                                                 private_key_path, "prometheus")
        if not is_tritonserver_existing:
            send_model_repository(instance_public_ip, private_key_path)
        if not is_prometheus_existing:
            send_prometheus_source(instance_public_ip, private_key_path)

        for i in range(1):
            status = instance_state(instance["InstanceId"])
            print(f'{colors.YELLOW}\tclient instance status:  ' +
                  f'{colors.RESET}{colors.MAGENTA}{status} ...{colors.RESET}')
            time.sleep(1)
        send_info("triton_instances_info.csv", "client_instance_info.csv")
        if instance_public_ip:
            time.sleep(5)
            gpu_info = instance_gpus(instance["InstanceId"])
            gpus = 0
            if gpu_info['count'] is not None:
                gpus = gpu_info['count']
            start_tritonserver(instance_public_ip, private_key_path, gpus=gpus)
            start_prometheus(instance_public_ip, private_key_path)
        else:
            print("Instance does not have public IP address")
    return triton_instances_info


def stop_server(filtered_instances, triton_instances_info,
                private_key_path="PATH_TO_AWS_KEY",
                aws_region="us-east-2"):
    """
    Stop the instances, tritonserver, and prometheus on the instances
    """
    for instance in filtered_instances:
        instance_public_ip = instance.get("PublicIpAddress", None)
        if instance_public_ip is not None:
            kill_tritonserver(instance_public_ip, private_key_path)
            kill_prometheus(instance_public_ip, private_key_path)
        status = instance_state(instance["InstanceId"])
        if status != "terminated":
            instance = stop_instance(instance["InstanceId"])
            triton_instances_info = update_info("triton_instances_info.csv",
                                                triton_instances_info,
                                                instance[0])
        for i in range(1):
            if len(instance) == 1:
                instance = instance[0]
            print(instance)
            status = instance_state(instance["InstanceId"])
            print(f'{colors.YELLOW}\tclient instance status:  ' +
                  f'{colors.RESET}{colors.MAGENTA}{status} ...{colors.RESET}')
            time.sleep(1)
        send_info("triton_instances_info.csv", "client_instance_info.csv")
    return triton_instances_info


def terminate_server(filtered_instances, triton_instances_info):
    """
    Terminate the instances, tritonserver, and prometheus on the instances
    """
    for instance in filtered_instances:
        terminate_instance(instance)
        triton_instances_info = remove_info("triton_instances_info.csv",
                                            triton_instances_info,
                                            instance["InstanceId"])
        send_info("triton_instances_info.csv", "client_instance_info.csv")
    return triton_instances_info
