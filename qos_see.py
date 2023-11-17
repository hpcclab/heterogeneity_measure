import pandas as pd
import numpy as np
from scipy.stats import hmean, gmean
from math import ceil
import os
import matplotlib.pyplot as plt
import seaborn as sns


def calc_eet(instance_code, experiment):
    path_to_file = f"analysis/results/{experiment}/{instance_code}"
    result_files = os.listdir(path_to_file)
    task_types = ['image_classification', 'object_detection',
                  'question_answering', 'speech_recognition']
    machine_types = ['t2.large',  'c5.2xlarge', 'g4dn.xlarge']
    eet = pd.DataFrame(columns=machine_types, index=task_types)
    for file in result_files:
        results = pd.read_csv(f'{path_to_file}/{file}')
        machines = results['assigned_machine'].unique()
        task_types = results['task_type'].unique()
        workload_eet = pd.DataFrame(columns=machines, index=task_types)
        for task_type in task_types:
            for machine in machines:
                eet_ij = results.loc[(results['task_type'] == task_type) &
                                     (results['assigned_machine'] == machine)]
                workload_eet.loc[task_type, machine] = eet_ij['inference_time'].mean()
        for column in workload_eet.columns:
            workload_eet.rename(columns={column: f"{column.split('_')[1]}.{column.split('_')[2]}"},
                                inplace=True)
        workload_eet = workload_eet.groupby(workload_eet.columns, axis=1).mean()
        eet = pd.concat([eet, workload_eet], axis=1)
    eet = eet.dropna(axis=1)
    eet = eet.groupby(eet.columns, axis=1).mean()
    return eet


def generate_eet_for_instances(eet_source, instance_code):
    instances = {'t2.large': int(instance_code.split('_')[0]),
                 'c5.2xlarge': int(instance_code.split('_')[1]),
                 'g4dn.xlarge': int(instance_code.split('_')[2])
                 }
    generated_eet = pd.DataFrame(index=eet_source.index.values)
    for instance_type, count in instances.items():
        for i in range(count):
            generated_eet[f'{instance_type}-{i+1}'] = eet_source[instance_type]
    return generated_eet


def calculate_see(eet, method='mixed'):
    if method == 'mixed':
        S_T = eet.max(axis=0) / eet
        S_M = eet.divide(eet.max(axis=1), axis=0)
        S_M = 1 / S_M
        weights = np.zeros(S_M.shape)
        s = S_M.sum(axis=1)
        for i in range(S_M.shape[0]):
            for j in range(S_M.shape[1]):
                weights[i, j] = S_M.iloc[i, j]/s[i]
        S_T_AVG = hmean(S_T, weights=weights, axis=0)
        eet_T_star = eet.max(axis=0)/S_T_AVG
        S_M = eet_T_star.divide(eet_T_star.max())
        S_M = 1 / S_M
        S_M_AVG = np.mean(S_M)
        SEE = eet_T_star.max()/S_M_AVG
    elif method == 'arithmetic':
        SEE = eet.mean().mean()
    elif method == 'geometric':
        SEE = gmean(gmean(eet))
    elif method == 'harmonic':
        SEE = hmean(hmean(eet))

    return SEE


def calc_true_qos(deadline, instance_code, experiment):
    qoss = []
    for i in range(1, 6):
        result = pd.read_csv(f"./analysis/results/{experiment}/" +
                             f"{instance_code}/{i}.csv")
        result = result.sort_values(by='completion_time')
        result['deadline'] = result['arrival_time'] + deadline
        qos = result['completion_time'].loc[result['deadline'] >= result['completion_time']].count()
        qos = round(100*(qos / result.shape[0]),1)
        qoss.append(qos)
    mean_qos = np.mean(qoss)
    return round(mean_qos)


def calc_estimated_qos(see, deadline, total_instances, total_tasks):
    estimated_qos = max(round( total_instances*deadline / (see*total_tasks) ,1), 100)
    return round(estimated_qos)


def create_see_qos_table(experiment, deadline, method='mixed', save_eet=False):
    instance_codes = os.listdir(f'./analysis/results/{experiment}/')
    errors = []
    df = pd.DataFrame(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge', 'ssee',
                               'estimated_qos', 'true_qos', 'err'])
    for idx, instance_code in enumerate(instance_codes):
        print(f"{idx}: Calculating for {instance_code}")
        source_eet = calc_eet(instance_code, experiment=experiment)
        eet = generate_eet_for_instances(source_eet, instance_code)
        # see = calculate_see(eet)
        see = calculate_see(eet, method=method)
        true_qos = calc_true_qos(deadline, instance_code, experiment=experiment)
        total_instances = sum([int(i) for i in instance_code.split('_')])
        ssee = round(see / total_instances)
        estimated_qos = calc_estimated_qos(see, deadline, total_instances, 1000)
        if true_qos > 0:
            err = (abs(true_qos-estimated_qos)/true_qos)*100
        else:
            err = abs(estimated_qos)
        errors.append(err)
        eet = eet.rename_axis('task_type')
        if save_eet:
            os.makedirs(f'analysis/results/eets/{experiment}', exist_ok=True)
            eet.to_csv(f'./analysis/results/eets/{experiment}/eet_{instance_code}.csv', index=True)
        d = {'t2.large': int(instance_code.split('_')[0]),
             'c5.2xlarge': int(instance_code.split('_')[1]),
             'g4dn.xlarge': int(instance_code.split('_')[2]),
             'ssee': round(ssee, 2),
             'estimated_qos': estimated_qos,
             'true_qos': true_qos,
             'err': round(err, 1)
             }
        df = pd.concat([df, pd.DataFrame(d, index=[0])], ignore_index=True)
    df = df.sort_values(by='ssee')
    os.makedirs(f'analysis/tables/{experiment}', exist_ok=True)
    df.to_csv(f'analysis/tables/{experiment}/see_qos_{method}.csv', index=False)
    print(f"Mean error: {np.mean(errors):0.1f}")
    return df


def simulation(experiment, method='mixed'):
    path_to_results = f'./analysis/{experiment}/results/simulation'
    instance_codes = os.listdir(path_to_results)
    results = pd.DataFrame(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge', 'ssee',
                                    'simulated_makespan'])
    for instance_code in instance_codes:
        source_eet = calc_eet(instance_code)
        eet = generate_eet_for_instances(source_eet, instance_code)
        see = calculate_see(eet, method=method)
        total_instances = sum([int(i) for i in instance_code.split('_')])
        ssee = round(see / total_instances)

        result = pd.read_csv(f"{path_to_results}/{instance_code}/FCFS_NQ/detailed-0.csv",
                             usecols=['completion_time'])
        result = result.sort_values(by='completion_time')
        makespan = result["completion_time"].iloc[-1]
        makespan = makespan/1000
        d = {'t2.large': int(instance_code.split('_')[0]),
             'c5.2xlarge': int(instance_code.split('_')[1]),
             'g4dn.xlarge': int(instance_code.split('_')[2]),
             'ssee': round(ssee, 2),
             'simulated_makespan': makespan
             }
        results = pd.concat([results, pd.DataFrame(d, index=[0])], ignore_index=True)
    results = results.sort_values(by='ssee')
    results.to_csv(f'analysis/tables/{experiment}/simulation_{method}.csv', index=False)
    return results

# method = 'harmonic'
# results = create_see_makespan_table(method=method, save_eet=False)


experiment = 'experiment_1_hete'
last_arrival_time = 25000.0
colors = ['red', 'blue', 'olive', 'purple']
markers = ['<', 's', 'v', 'D']
# methods = ['arithmetic', 'geometric', 'harmonic', 'mixed']
methods = ['mixed']
for i, method in enumerate(methods):
    results = create_see_qos_table(experiment=experiment, deadline=100,
                                   method=method, save_eet=False)
    path_to_table = f'./analysis/tables/{experiment}/see_qos_{method}.csv'
    results = pd.read_csv(path_to_table)
    plt.figure()
    sns.lineplot(data=results, x='ssee', y='estimated_qos',
                 marker=markers[i], markersize=7,
                 color=colors[i], linestyle='--', alpha=0.6,
                 label=f'estimated qos - {method}')
    sns.lineplot(data=results, x='ssee', y='true_qos',
                 marker='o', markersize=8, color='orange',
                 label='true qos')
    # simulation_results = simulation(method=method)
    # simulation_results = pd.read_csv(f'./analysis/tables/simulation_{method}.csv')
    # sns.lineplot(data=simulation_results, x='ssee', y='simulated_makespan',
    #              marker='*', markersize=6, markerfacecolor='darkred',
    #              markeredgecolor='darkred', markeredgewidth=1,
    #              color='darkred', linestyle=':',
    #              label=f'simulated makespan- {method}')
    plt.xlabel('S-SEE')
    plt.ylabel('makespan (s)')
    # plt.ylim(0, 100)
    os.makedirs(f'analysis/figures/{experiment}', exist_ok=True)
    plt.savefig(f'./analysis/figures/{experiment}/makespan_qos_{method}.png', dpi=600)
    plt.show()
