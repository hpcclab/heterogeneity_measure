import pandas as pd

results = pd.read_csv('analysis/summary_not_filtered.csv')

# df = results.loc[(results['t2.large'] == 0) & (results['c5.2xlarge'] == 0) & (results['g4dn.xlarge'] == 0)]
df = results.loc[(results['t2.large'] == 1) & (results['c5.2xlarge'] == 5) & (results['g4dn.xlarge'] == 2)]
print(df)