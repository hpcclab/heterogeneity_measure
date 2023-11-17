'''
This file contains the code for the cost optimization analysis. The code takes the results of
running a bag of task on t2.large and g4dn.xlarge instance types and determines cost-efficient
configuration for this workload.
'''

import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.patches import Rectangle


def read_results(path_to_results='analysis/results/experiment_1_hete'):
    instance_codes = os.listdir(path_to_results)
    results = pd.DataFrame(columns=['t2.large', 'g4dn.xlarge', 'price', 'throughput'])
    for instance_code in instance_codes:
        instances = {'t2.large': int(instance_code.split('_')[0]),
                     'c5.2xlarge': int(instance_code.split('_')[1]),
                     'g4dn.xlarge': int(instance_code.split('_')[2])
                     }
        if instances['c5.2xlarge'] != 0:
            continue
        path_to_file = f"{path_to_results}/{instance_code}"
        result_files = os.listdir(path_to_file)
        throughputs = []
        for file in result_files:
            result = pd.read_csv(f'{path_to_file}/{file}')
            throughput = result['completion_time'].count() / (0.001*result['completion_time'].max())
            throughputs.append(throughput)
        throughput = np.mean(throughputs)
        d = {'t2.large': instances['t2.large'],
             'g4dn.xlarge': instances['g4dn.xlarge'],
             'price': round(instances['t2.large']*0.0928 + instances['g4dn.xlarge']*0.526, 4),
             'throughput': round(throughput, 2)
             }
        results = pd.concat([results, pd.DataFrame(d, index=[0])], axis=0)
        results.to_csv('analysis/tables/experiment_1_hete/cost_optimization.csv', index=False)
    return results



threshold = 125.0
results = read_results()
results = results.sort_values(by=['throughput'])
satisfactory_throughput = results[results['throughput'] >= threshold]
min_price = satisfactory_throughput['price'].min()
min_price_config = satisfactory_throughput[satisfactory_throughput['price'] == min_price]
optimum_point = (min_price_config['throughput'].values[0], min_price_config['price'].values[0])

results = results.loc[(results['t2.large']<14) & (results['g4dn.xlarge']>0)]

for point in zip(results['throughput'], results['price']):
    if point == optimum_point:
        plt.scatter(point[0], point[1], color='yellow', marker='*', edgecolors='black', s=200)
        plt.annotate(f't2.large:{min_price_config["t2.large"].values[0]}' +
                     f'\ng4dn.xlarge:{min_price_config["g4dn.xlarge"].values[0]}',
                     xy=point, xytext=(8, -15), textcoords='offset points', ha='left', va='bottom')
    else:
        plt.scatter(point[0], point[1], color='red' if point[0] < threshold else 'green',
                    marker='x' if point[0] < threshold else 'o')

plt.xlabel('Throughput (tasks/s)')
plt.ylabel('Price ($/h)')
plt.savefig('analysis/figures/experiment_1_hete/cost_optimization_2.pdf', dpi=300, bbox_inches='tight')
plt.show()

prices = np.zeros((results['t2.large'].max()+1, results['g4dn.xlarge'].max()))    # 2D array of prices
throughputs = np.zeros((results['t2.large'].max()+1, results['g4dn.xlarge'].max()))    # 2D array of throughputs

for row in results.itertuples():
    if row[2] == 0 or row[1] > 13:
        continue
    prices[row[1], row[2]-1] = row[3]
    throughputs[row[1], row[2]-1] = row[4]

f, ax = plt.subplots()
ax = sns.heatmap(throughputs, cmap='hot_r', linewidths=0.5, annot=prices, fmt='.3f',
            cbar_kws={'label': 'throughput (tasks/s)'})

ax.add_patch(Rectangle((1, 0), 1, 1, fill=False, edgecolor='blue', lw=3))



plt.xticks(np.arange(0.5, throughputs.shape[1]+0.5, 1), np.arange(1, throughputs.shape[1]+1, 1))
plt.xlabel('Number of g4dn.xlarge')
plt.ylabel('Number of t2.large')
plt.savefig('analysis/figures/experiment_1_hete/cost_optimization_heatmap_2.pdf', dpi=300, bbox_inches='tight')
plt.show()
