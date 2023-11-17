"""

"""
import pandas as pd


def eet_item(task, machine):
    """
    This function is used to create an item in the EET table.
    """
    path_to_file = f"analysis/profiling/{task}/{machine}"
    eets = []
    for i in range(1, 11):
        results = pd.read_csv(f'{path_to_file}/{i}.csv', usecols=['inference_time'])
        eet = results['inference_time'].mean()
        eets.append(eet)
    eet = sum(eets)/len(eets)
    return round(eet)


tasks = ['image_classification', 'object_detection',
         'question_answering', 'speech_recognition']
machines = ['t2.large',  'c5.2xlarge',
            'g4dn.xlarge']

eet = pd.DataFrame(columns=machines, index=tasks)

for task in tasks:
    for machine in machines:
        eet[machine][task] = eet_item(task, machine)
print(eet)
eet.index.name = 'task_type'
eet.to_csv('analysis/eet.csv')