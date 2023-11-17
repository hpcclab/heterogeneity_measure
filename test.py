import pandas as pd
import numpy as np

completions = []
for i in range(1,11):
    df = pd.read_csv(f"analysis/1_0_4/{i}.csv")
    df = df.sort_values(by='completion_time')
    completion_time = df["completion_time"].iloc[-1]
    completions.append(completion_time)
print(np.mean(completions))
print(completions)

# df = pd.read_csv(f"analysis/1_0_3/1.csv")
# df_t2_large = df.loc[df['assigned_machine']=='triton_t2_large_7', :]
# df_t2_large.to_csv('analysis/df_t2_large.csv')
# print(df_t2_large.groupby('task_type').count())