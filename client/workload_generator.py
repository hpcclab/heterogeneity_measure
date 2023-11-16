
from workload.workload import Workload

scenario = 'experiment_1_hete'
workload_samples = 10

for workload_id in range(1,workload_samples+1):
    workload = Workload()
    workload.generate(scenario_name=scenario, workload_id=workload_id)
