import pandas as pd

instance_code = '1_1_2'
results = pd.read_csv(f'analysis/experiment_1_hete/{instance_code}/1.csv')
task_types = results['task_type'].unique()
machine_types = results['assigned_machine'].unique()
eet = pd.DataFrame(columns=machine_types,index=task_types)
# results = results.iloc[600:,:]
counts = pd.DataFrame(columns=machine_types, index=task_types)
for task_type in task_types:
    for machine_type in machine_types:
        df = results.loc[(results['task_type']==task_type) & (results['assigned_machine'] == machine_type)]
        #df.to_csv(f'analysis/eet_{task_type}_{machine_type}.csv')
        d = {
            'task_type': task_type,
            'machine_type': machine_type,
            'count': df["inference_time"].count(),
            'mean_inference_time': df["inference_time"].mean()
        }
        # counts = pd.concat([counts, pd.DataFrame(d, index=[0])], ignore_index=True)
        counts.loc[task_type,machine_type] = df.shape[0]
        eet.loc[task_type,machine_type] = results.loc[(results['task_type']==task_type) & (results['assigned_machine']==machine_type)]['inference_time'].mean()

eet = eet.round(0)
print(eet)
eet.to_csv(f'analysis/eet_{instance_code}_temp.csv')
counts.to_csv(f'analysis/counts_{instance_code}_temp.csv')



