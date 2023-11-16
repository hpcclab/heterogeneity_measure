"""
TODO: Add docstring
"""
import tritonclient.grpc.aio as grpcclient
import pandas as pd
import asyncio
import time
import os

from loadbalancer.FCFS import FCFS
from apps.speech_recognition import speech_recognition as spr
from apps.object_detection import object_detection as obd
from apps.image_classification import image_classification as ic
from apps.question_answering import question_answering as qa
from machine.machine_type import MachineType
from machine.machine import Machine
from task.task_type import TaskType
from task.task import Task
from colors import Colors


def read_workload(workload_file):
    workload = pd.read_csv(workload_file)
    tasks = []
    Task.id = 0
    for _, row in workload.iterrows():
        task_type = TaskType(row['task_type'])
        task = Task(
            task_type=task_type,
            arrival_time=row['arrival_time'],
            metadata=row['metadata'],
        )
        tasks.append(task)
    return tasks


async def infer(task, inputs, loadbalancer, start_time):
    await asyncio.sleep(task.arrival_time)

    assigned_machine, client = loadbalancer.get_client(task)
    while client == None:
        await asyncio.sleep(0.01)
        assigned_machine, client = loadbalancer.get_client(task)
    task.assigned_machine = assigned_machine
    task_type = task.type.name

    if task_type != 'question_answering':
        inputs = [inputs]
    s = time.perf_counter()
    await client.infer(model_name=task_type, inputs=inputs)
    e = time.perf_counter()
    task.makespan = e-s
    task.completion_time = e - start_time
    loadbalancer.queues[assigned_machine.name].remove(task)



def get_machines_info(instances_count):
    instances = pd.DataFrame(columns=['InstanceId', 'InstanceType',
                                      'InstanceName', 'PublicIpAddress'])
    pool = pd.read_csv('triton_instances_info.csv')
    for instance_type, count in instances_count.items():
        if count>0:
            filtered_pool = pool.loc[pool['InstanceType']==instance_type]
            if filtered_pool.shape[0] < count:
                raise ValueError(f'There is not enough number of instance of type {instance_type}')
            instances = pd.concat([instances, filtered_pool.head(count)], ignore_index=True)
    return instances


async def main_async(tasks, machines, inputs, start_time):
    queues = {}
    clients = {}
    for machine in machines:
        instance_ip = machine.instance_ip
        client = grpcclient.InferenceServerClient(url=f"{instance_ip}:8001")
        clients[machine.name] = client
        queues[machine.name] = []
    loadbalancer = FCFS()
    loadbalancer.clients = clients
    loadbalancer.machines = machines
    loadbalancer.queues = queues
    await asyncio.gather(*(infer(task, inputs[task.type.name], loadbalancer, start_time)
                           for task in tasks))


def main(workload_name, workload_id, instance_count, verbose=0):
    workload = pd.read_csv(f'workload/{workload_name}/workload-{workload_id}.csv')
    workload = pd.DataFrame(data=workload, columns=['task_type', 'arrival_time','metadata'])
    task_types = workload['task_type'].unique()
    tasks = []
    Task.id = 0
    for task_type in task_types:
        workload_for_task_type = workload.loc[workload['task_type']==task_type]
        tasks_for_task_type = []
        for _, row in workload_for_task_type.iterrows():
            task_type = TaskType(row['task_type'])
            task = Task(
                task_type=task_type,
                # arrival_time=row['arrival_time'],
                arrival_time=0.0,
                metadata=row['metadata'],
            )
            task.arrival_time = task.id * 0.0
            tasks_for_task_type.append(task)
        tasks.append(tasks_for_task_type)

    machines = []
    machines_info = get_machines_info(instances_count=instance_count)
    for _, row in machines_info.iterrows():
        machine_type = MachineType(row['InstanceType'])
        machine = Machine(
            instance_id=row['InstanceId'],
            name = row['InstanceName'],
            machine_type=machine_type,
            instance_ip=row['PublicIpAddress'],
        )
        machines.append(machine)
    inputs = {}
    inputs['object_detection'] = grpcclient.InferInput('images', [1, 3, 256, 256], "FP32")
    inputs['image_classification'] = grpcclient.InferInput('input', [1, 3, 224, 224], "FP32")
    inputs['question_answering'] = [grpcclient.InferInput('input_ids', [1, 35], "INT64"),
                                    grpcclient.InferInput('attention_mask', [1, 35], "INT64")]
    inputs['speech_recognition'] = grpcclient.InferInput('input', [1, 74400], "FP32")

    input_data = obd.preprocessing(f'./apps/object_detection/data/sample_image.jpg')
    inputs['object_detection'].set_data_from_numpy(input_data.numpy())

    input_data = spr.preprocessing(f'./apps/speech_recognition/data/sample_audio.wav')
    inputs['speech_recognition'].set_data_from_numpy(input_data.numpy())

    question = 'Why is model conversion important?'
    context = 'The option to convert models between FARM and ' + \
                'transformers gives freedom to the user and let people ' + \
                'easily switch between frameworks.'
    input_data = qa.preprocessing(question, context)
    inputs['question_answering'][0].set_data_from_numpy(input_data['input_ids'].numpy())
    inputs['question_answering'][1].set_data_from_numpy(input_data['attention_mask'].numpy())

    input_data = ic.preprocessing('./apps/image_classification/data/sample_image.jpg')
    inputs['image_classification'].set_data_from_numpy(input_data.numpy())

    report = pd.DataFrame(columns=['task_id', 'task_type', 'assigned_machine', 'arrival_time',
                                   'inference_time',  'completion_time'])

    if verbose:
        print(f"{Colors.BOLD}{Colors.YELLOW}"+96*u'\u2581'+f"{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}  ID {Colors.RESET}" +
            f"{Colors.BOLD}{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
            f"{Colors.BOLD}{Colors.GREEN}      Task Type     {Colors.RESET}" +
            f"{Colors.BOLD}{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
            f"{Colors.BOLD}{Colors.GREEN}   Machine   {Colors.RESET}" +
            f"{Colors.BOLD}{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
            f"{Colors.BOLD}{Colors.GREEN}  Arr. Time  {Colors.RESET}" +
            f"{Colors.BOLD}{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
            f"{Colors.BOLD}{Colors.GREEN} Infer. Time {Colors.RESET}" +
            f"{Colors.BOLD}{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
            f"{Colors.BOLD}{Colors.GREEN} Compl. Time {Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.YELLOW}"+96*u'\u2550'+f"{Colors.RESET}")

    start_time = time.perf_counter()
    for tasks_for_task_type in tasks:
        asyncio.run(main_async(tasks=tasks_for_task_type, machines=machines, inputs=inputs, start_time=start_time))

        if verbose:
            for task in tasks_for_task_type:
                machine_name = f"{task.assigned_machine.machine_type.name}"
                machine_name += f"-{task.assigned_machine.name.split('_')[-1]}"
                print(
                f"{Colors.GREEN}{str(task.id):^5s}{Colors.RESET}" +
                f"{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
                f"{Colors.GREEN}{str(task.type.name):^20s}{Colors.RESET}" +
                f"{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
                f"{Colors.GREEN}{machine_name:^13s}{Colors.RESET}" +
                f"{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
                f"{Colors.GREEN}{str(round(task.arrival_time*1000)):^13s}{Colors.RESET}" +
                f"{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
                f"{Colors.GREEN}{str(round(task.makespan*1000)):^13s}{Colors.RESET}" +
                f"{Colors.YELLOW}"+u'\u2595'+f"{Colors.RESET}" +
                f"{Colors.GREEN}{str(round(task.completion_time*1000)):^13s}{Colors.RESET}")

    for  tasks_for_task_type in tasks:
        for task in tasks_for_task_type:
            d = {'task_id': task.id,
                'task_type': task.type.name,
                'assigned_machine': f"{task.assigned_machine.name}",
                'arrival_time': round(task.arrival_time*1000),
                'inference_time': round(task.makespan*1000),
                'completion_time': round(task.completion_time*1000)}
            report = pd.concat([report, pd.DataFrame(d, index=[0])], ignore_index=True)
    report = report.sort_values('completion_time')
    if workload_name.split('_')[0] == 'profiling':
        task_type = tasks[0][0].type.name
        instance_type = machines_info.loc[0,'InstanceType']
        report_file_name = f"profiling_{task_type}_{instance_type}"
        report.to_csv(f'./reports/{report_file_name}.csv', index=False)
    else:
        system_id = f"{instance_count['t2.large']}_{instance_count['c5.2xlarge']}_{instance_count['g4dn.xlarge']}"
        if not os.path.exists(f"./reports/{workload_name}/{system_id}"):
            os.makedirs(f"./reports/{workload_name}/{system_id}")
        report_file_name = f'{workload_id}'
        report.to_csv(f'./reports/{workload_name}/{system_id}/{report_file_name}.csv', index=False)


if __name__=='__main__':
    hete_homo = 'hete'
    workload = f'experiment_1_{hete_homo}'
    see_table = pd.read_csv('./see_table.csv')
    for idx, row in see_table.iterrows():
        if hete_homo == 'homo':
            if int(row['t2.large']) != 0:
                instance_count = {'t2.large': int(row['total']),
                                'c5.2xlarge': 0,
                                'g4dn.xlarge': 0}
            elif int(row['c5.2xlarge']) != 0:
                instance_count = {'t2.large': 0,
                                'c5.2xlarge': int(row['total']),
                                'g4dn.xlarge': 0}
            elif int(row['g4dn.xlarge']) != 0:
                instance_count = {'t2.large': 0,
                                'c5.2xlarge': 0,
                                'g4dn.xlarge': int(row['total'])}
        elif hete_homo == 'hete':
            instance_count = {'t2.large': int(row['t2.large']),
                            'c5.2xlarge': int(row['c5.2xlarge']),
                            'g4dn.xlarge': int(row['g4dn.xlarge'])}

        print(f"{Colors.BOLD}{Colors.YELLOW}t2.large: {Colors.RESET}"+
            f"{Colors.MAGENTA}{int(row['t2.large'])}{Colors.RESET}"+
            f"{Colors.BOLD}{Colors.YELLOW} c5.2xlarge: {Colors.RESET}"+
            f"{Colors.MAGENTA}{int(row['c5.2xlarge'])}{Colors.RESET}"+
            f"{Colors.BOLD}{Colors.YELLOW} g4dn.xlarge: {Colors.RESET}"+
            f"{Colors.MAGENTA}{int(row['g4dn.xlarge'])}{Colors.RESET}")
        for i in range(1,6):
            main(workload_name=workload, workload_id=i, instance_count=instance_count, verbose=0)

# workload_name = f'experiment_1_large_task'
# workload_name = f'experiment_1_hete'
# instance_count = {'t2.large': 1,
#                           'c5.2xlarge': 0,
#                           'g4dn.xlarge': 4}
# for i in range(1,11):
#     main(workload_name=workload_name, workload_id=i, instance_count=instance_count)





