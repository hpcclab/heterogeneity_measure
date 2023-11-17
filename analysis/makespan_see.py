import pandas as pd
import numpy as np
from math import ceil
from scipy.stats import hmean
from numpy import mean
import matplotlib.pyplot as plt
import os
import seaborn as sns


def calculate_see(eet):
    # S_T = eet.max(axis=0) / eet
    # S_T_AVG = hmean(S_T)
    # eet_T_star = eet.max(axis=0)/S_T_AVG

    # S_M = eet_T_star.divide(eet_T_star.max())
    # S_M = 1 / S_M
    # S_M_AVG =mean(S_M)
    # SEE = eet_T_star.max()/S_M_AVG

    S_T = eet.max(axis=0) / eet
    S_M = eet.divide(eet.max(axis=1), axis=0)
    S_M = 1 / S_M

    weights = np.zeros(S_M.shape)
    s = S_M.sum(axis=1)
    for i in range(S_M.shape[0]):
        for j in range(S_M.shape[1]):
            weights[i,j] = S_M.iloc[i,j]/s[i]

    s = weights.sum(axis=0)
    for j in range(weights.shape[1]):
        for i in range(weights.shape[0]):
            weights[i,j] = weights[i,j]/ s[j]

    S_T_AVG = hmean(S_T, weights=weights, axis=0)
    eet_T_star = eet.max(axis=0)/S_T_AVG

    S_M = eet_T_star.divide(eet_T_star.max())
    S_M = 1 / S_M
    S_M_AVG =mean(S_M)
    SEE = eet_T_star.max()/S_M_AVG
    return SEE


def generate_eet(path_to_eet, instances):
    eet_source = pd.read_csv(path_to_eet, index_col='task_type')
    generated_eet = pd.DataFrame(index=eet_source.index.values)
    for instance_type, count in instances.items():
        for i in range(count):
            generated_eet[f'{instance_type}-{i+1}'] = eet_source[instance_type]
    return generated_eet


def calc_estimated_makespan(instances):
    eet = generate_eet('./analysis/eet.csv', instances)
    see = calculate_see(eet)
    total_number_of_machines = sum(instances.values())
    estimated_makespan = ceil(600/total_number_of_machines) * see
    return round(estimated_makespan)


def calc_true_makespan(instances):
    t2_large = instances['t2.large']
    c5_2xlarge = instances['c5.2xlarge']
    g4dn_xlarge = instances['g4dn.xlarge']
    makespans = []
    for i in range(1, 6):
        result = pd.read_csv("./analysis/experiment_1_hete/" +
                             f"{t2_large}_{c5_2xlarge}_{g4dn_xlarge}/{i}.csv")
        makespan = result["completion_time"].iloc[-1]
        makespans.append(makespan)
    makespan = np.mean(makespans)
    return round(makespan)


def system_makespan_see_table():
    systems = os.listdir('./analysis/experiment_1_hete/')
    summary = pd.DataFrame(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge', 'see',
                                    'estimated_makespan', 'true_makespan', 'err'])
    for system in systems:
        instances = {'t2.large': int(system.split('_')[0]),
                     'c5.2xlarge': int(system.split('_')[1]),
                     'g4dn.xlarge': int(system.split('_')[2])
                     }
        see = calculate_see(generate_eet('./analysis/eet.csv', instances))
        see = round(see / sum(instances.values()), 1)
        estimated_makespan = calc_estimated_makespan(instances)
        true_makespan = calc_true_makespan(instances)
        err = 100*(abs(true_makespan - estimated_makespan) / true_makespan)  # in percentage
        d = {'t2.large': instances['t2.large'],
             'c5.2xlarge': instances['c5.2xlarge'],
             'g4dn.xlarge': instances['g4dn.xlarge'],
             'see': see,
             'estimated_makespan': estimated_makespan,
             'true_makespan': true_makespan,
             'err': err}
        summary = pd.concat([summary, pd.DataFrame(d, index=[0])], ignore_index=True)
    summary = summary.sort_values(by=['see'])
    summary.to_csv('./analysis/summary_4.csv', index=False)
    return summary


def calc_expected_makespan_see(makespan_see_table):
    makespan_see_table = makespan_see_table.drop(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge'],
                                                 axis=1)
    makespan_see_table['estimated_makespan'] = makespan_see_table['estimated_makespan'].astype('float')
    makespan_see_table['true_makespan'] = makespan_see_table['true_makespan'].astype('float')
    expected_makespan_see = makespan_see_table.groupby(['see']).mean()
    expected_makespan_see = expected_makespan_see.reset_index()
    expected_makespan_see = expected_makespan_see.sort_values(by=['see'])
    expected_makespan_see.to_csv('./analysis/expected_makespan_see_4.csv')
    return expected_makespan_see


summary = system_makespan_see_table()
summary['total'] = summary['t2.large'] + summary['c5.2xlarge'] + summary['g4dn.xlarge']

summary.to_csv('./analysis/summary_not_filtered_4.csv', index=False)
# print(summary.shape)
# summary = summary.loc[summary['total'] >= 10, :]
summary = summary.drop(columns=['total'], axis=1)
see_counts = summary['see'].value_counts()
excluded_see = see_counts[see_counts < 2].index.values
summary = summary[~summary['see'].isin(excluded_see)]
# summary = summary.loc[summary['see'] != 13, :]  #
# summary = summary.loc[summary['see'] != 14, :]  #
# summary = summary.loc[summary['see'] != 17, :]  #
# summary = summary.loc[summary['see'] != 18, :]  #
# print(summary.shape)
summary.to_csv('./analysis/summary_4.csv', index=False)
expected_makespan_see = calc_expected_makespan_see(summary)



df = pd.read_csv('./analysis/summary_4.csv')

# df = df.loc[df['see'] != 9.9, :]  #
# df = df.loc[df['see'] != 9.3, :]  #
# df = df.loc[df['see'] != 8.8, :]  #
# df = df.loc[df['see'] != 18, :]  #

# print(df)
sns.set_style("whitegrid")
sns.lineplot(data=df, x='see', y='true_makespan', label='true makespan')
sns.lineplot(data=df, x='see', y='estimated_makespan', label='estimated makespan')
plt.savefig('./analysis/makespan_see_sns_4.png')
plt.show()

plt.figure()

# Calculate the average y for each x
averages_estimated = df.groupby('see')['estimated_makespan'].mean()

# Calculate the standard deviation for each x
std_devs_estimated = df.groupby('see')['estimated_makespan'].std(ddof=0)

# Calculate the number of samples for each x
sample_sizes = df.groupby('see')['estimated_makespan'].count()

# Calculate the standard error of the mean for each x
std_errors_estimated = std_devs_estimated / (sample_sizes**0.5)
print(averages_estimated, std_devs_estimated)

# Plot the average y values with confidence intervals
plt.errorbar(averages_estimated.index, averages_estimated, yerr=1.96*std_errors_estimated, fmt='o', capsize=5, color='blue')


plt.plot(averages_estimated.index.values, averages_estimated,
         label='estimated makespan', color='navy')



# Calculate the average y for each x
averages_true = df.groupby('see')['true_makespan'].mean()

# Calculate the standard deviation for each x
std_devs_true = df.groupby('see')['true_makespan'].std(ddof=0)

# Calculate the number of samples for each x
sample_sizes = df.groupby('see')['true_makespan'].count()

# Calculate the standard error of the mean for each x
std_errors_true = std_devs_true / (sample_sizes**0.5)
print(averages_true, std_devs_true)


# Plot the average y values with confidence intervals
plt.errorbar(averages_true.index, averages_true, yerr=1.96*std_errors_true, fmt='o', capsize=5, color='orange')


plt.plot(averages_true.index.values, averages_true,
         label='true makespan', color='red')


# plt.plot(df['see'], df['true_makespan'],
#          label='true_makespan')
plt.xlabel('SEE score')
plt.ylabel('makespan [ms]')
plt.legend()
plt.savefig('./analysis/makespan_see_4.png')
plt.show()