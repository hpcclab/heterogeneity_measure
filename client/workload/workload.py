"""
TODO: Add description of the class
"""
import numpy as np
import pandas as pd
import os

from workload.random_sample import RandomSample


class Workload:

    def __init__(self):
        self.workload = pd.DataFrame(columns=['task_type', 'arrival_time', 'metadata'])

    def reset(self):
        self.workload = pd.DataFrame(columns=['task_type', 'arrival_time', 'metadata'])

    def generate(self, scenario_name, workload_id, seed=100, precision=2):
        path_to_sc = f"./workload/scenarios/{scenario_name}.csv"
        scenario = pd.read_csv(path_to_sc)

        for idx, row in scenario.iterrows():
            task_type = row[0]
            start_time = row[1]
            end_time = row[2]
            dist = row[3]
            no_of_tasks = row[4]
            if task_type != 'question_answering':
                metadata_files = os.listdir(f"./apps/{task_type}/data/")
                metadata = np.random.choice(metadata_files, no_of_tasks)
            else:
                metadata = ''
            seed = seed + 10 * int(idx)
            print(f'{task_type} {dist}')
            sample = RandomSample(start_time, end_time, no_of_tasks, seed).generate(dist)
            df = pd.DataFrame({'arrival_time': sample, 'metadata': metadata})
            df['task_type'] = task_type
            self.workload = pd.concat([self.workload, df], ignore_index=True)

        self.workload = self.workload.sort_values(by=['arrival_time'])
        self.workload = self.workload.reset_index(drop=True)
        folder = f"./workload/{scenario_name}"
        os.makedirs(folder, exist_ok=True)
        path_to_output = f"{folder}/workload-{workload_id}.csv"
        self.workload.to_csv(path_to_output, index=False)
        return self.workload
