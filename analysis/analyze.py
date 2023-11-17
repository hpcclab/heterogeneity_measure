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


def calc_true_makespan(instance_code, experiment):
    makespans = []
    for i in range(1, 6):
        result = pd.read_csv(f"./analysis/results/{experiment}/" +
                             f"{instance_code}/{i}.csv")
        result = result.sort_values(by='completion_time')
        makespan = result["completion_time"].iloc[-1]
        makespans.append(makespan)
    makespan = np.mean(makespans)
    return round(makespan)


def calc_estimated_makespan(see, total_instances, total_tasks, last_arrival_time=0):
    estimated_makespan = max(ceil(total_tasks/total_instances) * see, last_arrival_time)
    return round(estimated_makespan)


def create_see_makespan_table(experiment, last_arrival_time, method='mixed', save_eet=False):
    instance_codes = os.listdir(f'./analysis/results/{experiment}/')
    errors = []
    df = pd.DataFrame(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge', 'ssee',
                               'estimated_makespan', 'true_makespan', 'err'])
    for idx, instance_code in enumerate(instance_codes):
        print(f"{idx}: Calculating for {instance_code}")
        source_eet = calc_eet(instance_code, experiment=experiment)
        eet = generate_eet_for_instances(source_eet, instance_code)
        # see = calculate_see(eet)
        see = calculate_see(eet, method=method)
        true_makespan = calc_true_makespan(instance_code, experiment=experiment)
        total_instances = sum([int(i) for i in instance_code.split('_')])
        ssee = round(see / total_instances)
        estimated_makespan = calc_estimated_makespan(see, total_instances, 1000,
                                                     last_arrival_time=last_arrival_time)
        err = (abs(true_makespan-estimated_makespan)/true_makespan)*100
        errors.append(err)
        eet = eet.rename_axis('task_type')
        if save_eet:
            os.makedirs(f'analysis/results/eets/{experiment}', exist_ok=True)
            eet.to_csv(f'./analysis/results/eets/{experiment}/eet_{instance_code}.csv', index=True)
        d = {'t2.large': int(instance_code.split('_')[0]),
             'c5.2xlarge': int(instance_code.split('_')[1]),
             'g4dn.xlarge': int(instance_code.split('_')[2]),
             'ssee': round(ssee, 2),
             'estimated_makespan': estimated_makespan,
             'true_makespan': true_makespan,
             'err': round(err, 1)
             }
        df = pd.concat([df, pd.DataFrame(d, index=[0])], ignore_index=True)
    df = df.sort_values(by='ssee')
    os.makedirs(f'analysis/tables/{experiment}', exist_ok=True)
    df.to_csv(f'analysis/tables/{experiment}/see_makespan_{method}.csv', index=False)
    print(f"Mean error: {np.mean(errors):0.1f}")
    return df


def simulation(experiment, method='mixed'):
    path_to_results = f'./analysis/results/simulation'
    instance_codes = os.listdir(path_to_results)
    results = pd.DataFrame(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge', 'ssee',
                                    'simulated_makespan'])
    for instance_code in instance_codes:
        source_eet = calc_eet(instance_code, 'simulation')
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
last_arrival_time = 0.0
# colors = { 'mixed':'blue', 'harmonic':'olive', 'arithmetic':'red', 'gemoetric':'purple' }
colors = { 'mixed':'orange', 'harmonic':'blue', 'arithmetic':'red', 'geometric':'purple', 'true':'olive' }
markers = {'geometric':'<', 'mixed':'s', 'harmonic':'v', 'arithmetic':'D', 'true':'o'}
methods = ['arithmetic', 'geometric', 'harmonic', 'mixed']
methods = ['geometric']
# methods = ['mixed']
for i, method in enumerate(methods):
    # results = create_see_makespan_table(experiment=experiment, last_arrival_time=last_arrival_time,
    #                                     method=method, save_eet=True)
    path_to_table = f'./analysis/tables/{experiment}/see_makespan_{method}.csv'
    results = pd.read_csv(path_to_table)
    results['true_makespan'] = results['true_makespan']/1000
    results['estimated_makespan'] = results['estimated_makespan']/1000
    results['true_throughput'] = 1000 / results['true_makespan']
    results['estimated_throughput'] = 1000 / results['estimated_makespan']
    if method == 'mixed':
        method_label = 'hybrid'
    else:
        method_label = method
    plt.figure()
    sns.lineplot(data=results, x='ssee',
                #  y='estimated_throughput',
                y='estimated_makespan',
                 marker=markers[method], markersize=9,
                 color=colors[method], linestyle='--', alpha=0.6,
                 label=f'estimated:{method_label}', zorder=10)

    simulation_results = pd.read_csv(f'./analysis/tables/{experiment}/simulation_{method}.csv')
    simulation_results['simulated_throughput'] = 1000 / simulation_results['simulated_makespan']

    sns.lineplot(data=simulation_results, x='ssee',
                #  y='simulated_throughput',
                y='simulated_makespan',
                 marker='x', markersize=6, markerfacecolor='darkred',
                 markeredgecolor='darkred', markeredgewidth=2,
                 color='darkred', linestyle=':',
                 label='simulated')



    sns.lineplot(data=results, x='ssee',
                #  y='true_throughput',
                y='true_makespan',
                 marker=markers['true'], markersize=8, color=colors['true'],
                 label='true value')

    plt.xlabel(r'$\widebar{eet}_{geometric}$', fontsize=14)
    # plt.xlabel('S-HEET', fontsize=14)
    plt.ylabel('makespan (s)', fontsize=14)
    # plt.ylabel('throughput (tasks/s)', fontsize=14)
    # plt.ylim(0, 30)
    plt.legend(fontsize=14, frameon=False)
    os.makedirs(f'analysis/figures/{experiment}', exist_ok=True)
    # plt.savefig(f'./analysis/figures/{experiment}/throughput_see_{method}.pdf', dpi=300)
    plt.savefig(f'./analysis/figures/{experiment}/makespan_see_{method}.pdf', dpi=300)
    plt.show()
