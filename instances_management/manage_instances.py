"""
TODO: Add docstring
"""
import subprocess
import json
import time
import yaml
import pandas as pd
from colors import colors


def existing_instances(tag_prefix='triton'):
    command = 'aws ec2 describe-instances'
    command += ' --query "Reservations[*].Instances[*].'
    command += '{ InstanceId: InstanceId, PublicIpAddress: PublicIpAddress, Tags: Tags,'
    command += 'InstanceType: InstanceType}"'
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        instances = json.loads(completed_process.stdout)
        filtered_instances = []
        for instance in instances:
            if len(instance) > 1:
                for instance_replica in instance:
                    tags = instance_replica.get("Tags", [])
                    if tags is not None:
                        for tag in tags:
                            if tag.get("Key") == "Name" and tag.get("Value").startswith(tag_prefix):
                                filtered_instances.append(instance_replica)
                                break
            else:
                instance = instance[0]
                tags = instance.get("Tags", [])
                if tags is not None:
                    for tag in tags:
                        if tag.get("Key") == "Name" and tag.get("Value").startswith(tag_prefix):
                            filtered_instances.append(instance)
                            break
        return filtered_instances
    else:
        print(f"{colors.BOLD}{colors.RED}Error: {completed_process.stderr}{colors.RESET}")


def instance_info(instance_id):
    command = 'aws ec2 describe-instances'
    command += f' --instance-ids {instance_id}'
    command += ' --query "Reservations[*].Instances[*].'
    command += '{ InstanceId: InstanceId, PublicIpAddress: PublicIpAddress, Tags: Tags,'
    command += 'InstanceType: InstanceType}"'
    completed_process = subprocess.run(command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        instance = json.loads(completed_process.stdout)
        return instance[0]
    else:
        print(f"Error: {completed_process.stderr}")


def instance_gpus(instance_id):
    aws_command = f'aws ec2 describe-instances --instance-ids {instance_id}'
    aws_command += ' --query "Reservations[*].Instances[*].InstanceType"'
    aws_command += ' --output text'
    completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        instance_type = completed_process.stdout
        instance_type = instance_type.strip()
        aws_command = f'aws ec2 describe-instance-types --instance-types {instance_type}'
        aws_command += ' --query "InstanceTypes[*].{count:GpuInfo.Gpus[0].Count,'
        aws_command += ' brand:GpuInfo.Gpus[0].Manufacturer,'
        aws_command += ' memory: GpuInfo.Gpus[0].MemoryInfo.SizeInMiB,'
        aws_command += ' name:GpuInfo.Gpus[0].Name}"'
        completed_subprocess = subprocess.run(aws_command, shell=True,
                                              capture_output=True, text=True)
        if completed_subprocess.returncode == 0:
            gpuinfo = json.loads(completed_subprocess.stdout)
            return gpuinfo[0]
        else:
            print(f"{colors.BOLD}{colors.RED}Error: {completed_subprocess.stderr}{colors.RESET}")
    else:
        print(f"{colors.BOLD}{colors.RED}Error: {completed_process.stderr}{colors.RESET}")


def instance_name(instance):
    tags = instance.get("Tags", [])
    for tag in tags:
        if tag.get("Key") == "Name":
            return tag.get("Value")
    return None


def instance_state(instance_id):
    aws_command = 'aws ec2 describe-instance-status --include-all-instances '
    aws_command += f'--instance-ids {instance_id}'
    process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if process.returncode == 0:
        response = json.loads(process.stdout)
        status = response['InstanceStatuses'][0]['InstanceState']['Name']
        return status
    else:
        print(f"{colors.BOLD}{colors.RED}Error: {status.stderr}{colors.RESET}")


def start_instance(aws_region, instance_id):
    status = instance_state(instance_id)
    instance = instance_info(instance_id=instance_id)[0]
    if status == "running":
        print(f"{colors.BOLD}{colors.YELLOW}WARNING:{colors.RESET}{colors.YELLOW} Instance " +
              f"{colors.RESET}[id:]{colors.MAGENTA}{instance_id} {colors.RESET}" +
              f"[name:]{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"{colors.YELLOW}is already running!{colors.RESET}")
        return instance_info(instance_id=instance_id)
    elif status == "pending":
        print(f"{colors.BOLD}{colors.YELLOW}WARNING: {colors.RESET}{colors.YELLOW} Instance " +
              f"{colors.RESET}[id:]{colors.MAGENTA}{instance_id} {colors.RESET}" +
              f"[name:]{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"{colors.YELLOW}is already pending!{colors.RESET}")
        while status != "running":
            time.sleep(1)
            status = instance_state(instance_id)
        print(f"{colors.BOLD}{colors.GREEN}Instance " +
              f"successfully started and ready to use!{colors.RESET}")
        return instance_info(instance_id=instance_id)
    elif status in ["terminated", "shutting-down"]:
        print(f"{colors.BOLD}{colors.RED}ERROR:{colors.RESET}{colors.RED} Instance " +
              f"{colors.RESET}[id:]{colors.MAGENTA}{instance_id} {colors.RESET}" +
              f"[name:]{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"{colors.RED}has been already terminated!{colors.RESET}")
        return instance_info(instance_id=instance_id)

    print(f"{colors.BOLD}{colors.CYAN}Starting instance:{colors.RESET}\n" +
          f"id:{colors.MAGENTA}{instance_id}{colors.RESET} " +
          f"name:{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
          f"type:{colors.MAGENTA}{instance['InstanceType']}{colors.RESET}{colors.RESET}")

    aws_command = f'aws ec2 start-instances --region {aws_region}'
    aws_command += f' --instance-ids {instance_id}'
    completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        status = instance_state(instance_id)
        while status != "running":
            time.sleep(2)
            status = instance_state(instance_id)
        print(f"{colors.BOLD}{colors.GREEN}Instance " +
              f"successfully started and ready to use!{colors.RESET}")
        return instance_info(instance_id=instance_id)
    else:
        print(f"{colors.BOLD}{colors.RED}Error: {completed_process.stderr}{colors.RESET}")


def stop_instance(instance_id):
    status = instance_state(instance_id)
    instance = instance_info(instance_id=instance_id)[0]
    if status == "stopped":
        print(f"{colors.BOLD}{colors.YELLOW}WARNING:{colors.RESET}{colors.YELLOW} Instance " +
              f"{colors.RESET}[id:]{colors.MAGENTA}{instance_id} {colors.RESET}" +
              f"[name:]{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"{colors.YELLOW}is already stopped!{colors.RESET}")
        return instance_info(instance_id=instance_id)
    elif status == "stopping":
        while status != "stopped":
            time.sleep(1)
            status = instance_state(instance_id)

        print(f"{colors.BOLD}{colors.YELLOW}WARNING:{colors.RESET}{colors.YELLOW} Instance " +
              f"{colors.RESET}[id:]{colors.MAGENTA}{instance_id} {colors.RESET}" +
              f"[name:]{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"{colors.YELLOW}is already stopping!{colors.RESET}")
        return instance_info(instance_id=instance_id)
    elif status == "terminated":
        print(f"{colors.BOLD}{colors.RED}ERROR:{colors.RESET}{colors.RED} Instance " +
              f"{colors.RESET}[id:]{colors.MAGENTA}{instance_id} {colors.RESET}" +
              f"[name:]{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"{colors.RED}has been already terminated!{colors.RESET}")
        return instance_info(instance_id=instance_id)

    elif status in ["running", "pending"]:
        print(f"{colors.BOLD}{colors.CYAN}Stopping instance:{colors.RESET}\n" +
              f"id:{colors.MAGENTA}{instance_id}{colors.RESET} " +
              f"name:{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
              f"type:{colors.MAGENTA}{instance['InstanceType']}{colors.RESET}{colors.RESET}")

        aws_command = f'aws ec2 stop-instances --instance-ids {instance_id}'
        completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
        if completed_process.returncode == 0:
            status = instance_state(instance_id)
            while status != "stopped":
                time.sleep(2)
                status = instance_state(instance_id)
            print(f"{colors.BOLD}{colors.GREEN}Instance successfully stopped{colors.RESET}")
            return instance_info(instance_id=instance_id)
        else:
            print(f"{colors.BOLD}{colors.RED}Error: {completed_process.stderr}{colors.RESET}")

    elif status in ["shuttingdown", "terminated"]:
        print(f"{colors.BOLD}{colors.YELLOW}WARNING: instance has been already terminated" +
              f"{colors.RESET}")


def terminate_instance(instance):
    instance_id = instance.get("InstanceId")
    aws_command = 'aws ec2 terminate-instances'
    aws_command += f' --instance-ids {instance_id}'
    print(f"{colors.BOLD}{colors.RED}Terminating instance:{colors.RESET}\n" +
          f"\tid:{colors.MAGENTA}{instance_id}{colors.RESET} " +
          f"\tname:{colors.MAGENTA}{instance_name(instance)}{colors.RESET} " +
          f"\ttype:{colors.MAGENTA}{instance['InstanceType']}{colors.RESET}{colors.RESET}")
    completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        response = json.loads(completed_process.stdout)
        status = response.get("TerminatingInstances")[0].get("CurrentState").get("Name")
        while status != "terminated":
            time.sleep(1)
            status = instance_state(instance_id)
        print(f"{colors.BOLD}{colors.GREEN}\t:: instance " +
              f"({colors.MAGENTA}{instance_id}{colors.RESET}) " +
              f"{colors.BOLD}{colors.GREEN}successfully terminated{colors.RESET}")
        return status
    else:
        print(f"{colors.BOLD}{colors.RED}Error: {completed_process.stderr}{colors.RESET}")


def get_image_id(instance_type):
    aws_command = 'aws ec2 describe-images '
    aws_command += f'--filters "Name=name,Values={instance_type}" '
    aws_command += '--query "Images[*].{ImageId:ImageId}"'
    completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        images = json.loads(completed_process.stdout)
        return images[0].get("ImageId")
    else:
        print(f"Error: {completed_process.stderr}")


def create_tags(instance_id, name):
    aws_command = f'aws ec2 create-tags --resources {instance_id} '
    aws_command += f'--tags Key=Name,Value={name}'
    completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        print(f"{colors.CYAN}\ttag name with value {name} for instance " +
              f"({colors.MAGENTA}{instance_id}{colors.RESET}) " +
              f"{colors.CYAN}successfully created!{colors.RESET}")
    else:
        print(f"Error: {completed_process.stderr}")


def launch(instance_type, count=1, starting_count=1,
           key_pair="Ali_AWS",
           security_group_id="sg-01c4cd01ef7aba06e"):
    print(f"{colors.BOLD}Launching {colors.MAGENTA}{count}{colors.RESET} of " +
          f"{colors.MAGENTA}{instance_type}{colors.RESET} {colors.BOLD}instances...{colors.RESET}")
    image_id = get_image_id(instance_type)
    print(f"{colors.YELLOW}\tAMI name: {instance_type} AMI ID: {image_id}{colors.RESET}")
    print(f"{colors.YELLOW}\tkey pair name: {key_pair}{colors.RESET}")
    print(f"{colors.YELLOW}\tsecurity group id: {security_group_id}{colors.RESET}")
    aws_instance_type = instance_type.split('_')[0]+'.'+instance_type.split('_')[1]
    aws_command = f'aws ec2 run-instances --image-id {image_id} '
    aws_command += f'--count {count} --instance-type {aws_instance_type} '
    aws_command += '--region us-east-2 '
    aws_command += f'--key-name {key_pair} '
    aws_command += f'--security-group-ids {security_group_id} '
    aws_command += '--output json'
    completed_process = subprocess.run(aws_command, shell=True, capture_output=True, text=True)
    if completed_process.returncode == 0:
        instances = json.loads(completed_process.stdout)
        for _, instance in enumerate(instances['Instances']):
            instance_id = instance['InstanceId']
            print(f"{colors.BOLD}{colors.GREEN}:: instance {starting_count} ({colors.MAGENTA}{instance_id}" +
                  f"{colors.GREEN}) successfully launched!{colors.RESET}")
            name = f"triton_{instance_type}_{starting_count}"
            starting_count += 1

            for i in range(5):
                status = instance_state(instance_id)
                print(f"{colors.YELLOW}\tinstance state: {status}{colors.RESET}")
                time.sleep(1)
            create_tags(instance_id, name)
        return instances
    else:
        print(f"Error: {completed_process.stderr}")


def count_instance_types():
    instances = existing_instances(tag_prefix="triton")
    counts = pd.DataFrame(columns=['instance_type', 'count'])
    for instance in instances:
        state = instance_state(instance['InstanceId'])
        if state != 'terminated':
            instance_count = pd.DataFrame({'instance_type': instance['InstanceType'], 'count': 1},
                                          index=[0])
            counts = pd.concat([counts, instance_count], ignore_index=True)
    counts = counts.groupby(['instance_type']).sum()
    return counts


def read_config(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    return config['instances']


def create_instances(path_to_config, ignore_existing=False):
    instances = read_config(path_to_config)
    for instance in instances:
        instance_type = instance['type']
        instance_type = instance_type.replace('_', '.')
        count = instance['count']
        existing_instance_types = count_instance_types()
        if (not ignore_existing) and (instance_type in existing_instance_types.index.values):
            existing_instances = existing_instance_types.loc[instance_type, 'count']
            print(f"{colors.YELLOW}\t:: ({colors.RESET}{colors.MAGENTA}{existing_instances}" +
                  f"{colors.RESET}{colors.YELLOW}) instance type {instance_type} " +
                  f"already exists!{colors.RESET}")
            count = count - existing_instances
        if count > 0:
            instance_type = instance_type.replace('.', '_')
            launch(instance_type, count, starting_count=existing_instances+1)
