import pandas as pd

instances = pd.read_csv('./triton_instances_info.csv')
client = pd.read_csv('./client_instance_info.csv')
instances = pd.concat([instances, client], ignore_index=True)

with open('/home/user.ssh/config', 'w') as f:
    for _, instance in instances.iterrows():
        print(f"instance name: {instance['InstanceName']} " +
              f"ip: {instance['PublicIpAddress']}")
        f.write(f"Host {instance['InstanceName']}\n")
        f.write(f"    HostName {instance['PublicIpAddress']}\n")
        f.write("    User ubuntu\n")
        f.write("    IdentityFile PATH_TO_AWS_KEY\n")

