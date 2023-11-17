"""
TODO: Add docstring
"""

import pandas as pd
from scipy.stats import hmean
from numpy import mean
import tqdm
import numpy as np


def calculate_see(eet):
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
    S_M_AVG = mean(S_M)
    SEE = eet_T_star.max()/S_M_AVG
    return SEE


def generate_eet(path_to_eet, instances):
    eet_source = pd.read_csv(path_to_eet, index_col='task_type')
    generated_eet = pd.DataFrame(index=eet_source.index.values)
    for instance_type, count in instances.items():
        for i in range(count):
            generated_eet[f'{instance_type}-{i+1}'] = eet_source[instance_type]
    return generated_eet


instances = {'t2.large': 1,
             'c5.2xlarge': 1,
             'g4dn.xlarge': 2
             }
# eet = generate_eet('analysis/eet_2.csv', instances)
eet = pd.read_csv('analysis/eet_1_1_2_temp.csv', index_col='task_type')
see = calculate_see(eet)
print(see)


# see_table = pd.DataFrame(columns=['t2.large', 'c5.2xlarge', 'g4dn.xlarge',
#                                   'total', 'price', 'see'])
# instances_limit = {'t2.large': 16,
#                    'c5.2xlarge': 4,
#                    'g4dn.xlarge': 3
#                    }
# inctance_price = {'t2.large': 0.0928,
#                   'c5.2xlarge': 0.34,
#                   'g4dn.xlarge': 0.526
#                   }
# total = (instances_limit['t2.large']+1) * (instances_limit['c5.2xlarge']+1) * \
#     (instances_limit['g4dn.xlarge']+1)
# i = 0
# pbar = tqdm.tqdm(total=total)
# for count_t2_large in range(instances_limit['t2.large']+1):
#     for count_c5_2xlarge in range(instances_limit['c5.2xlarge']+1):
#         for count_g4dn_xlarge in range(instances_limit['g4dn.xlarge']+1):
#             total = count_t2_large + count_c5_2xlarge + count_g4dn_xlarge
#             if total == 0 or total > 16:
#                 pbar.update(1)
#                 continue
#             instances = {'t2.large': count_t2_large,
#                          'c5.2xlarge': count_c5_2xlarge,
#                          'g4dn.xlarge': count_g4dn_xlarge
#                          }
#             eet = generate_eet('analysis/eet.csv', instances)
#             see = calculate_see(eet)
#             price = count_t2_large * inctance_price['t2.large'] + \
#                 count_c5_2xlarge * inctance_price['c5.2xlarge'] + \
#                 count_g4dn_xlarge * inctance_price['g4dn.xlarge']
#             instances['total'] = total
#             instances['price'] = round(price, 2)
#             instances['see'] = round(see/total)
#             see_table = pd.concat([see_table, pd.DataFrame(instances, index=[0])],
#                                   ignore_index=True)
#             pbar.update(1)
# see_table = see_table.sort_values('see')
# see_counts = see_table['see'].value_counts()
# excluded_see = see_counts[see_counts < 5].index.values
# see_table = see_table[~see_table['see'].isin(excluded_see)]
# see_table.to_csv('analysis/see_table.csv', index=False)
