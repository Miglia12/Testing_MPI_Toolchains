import reframe as rfm
import json

class OSU_Micro_Benchmark(rfm.RunOnlyRegressionTest):

    def __init__(self):
        self.valid_systems = ['aion:batch']  # This must match the system and partition name in the config file
        self.valid_prog_environs = ['gnu']   # This must match the desired environment in the config file
        self.num_tasks = 2                   # Set the tasks
        self.num_tasks_per_node = 2

        with open('paths.json', 'r') as file:
            self.paths = json.load(file) 

    @run_before('run')
    def set_computational_resources(self):
        self.job.options = [
            '--time=00:05:00',
            '--nodes=1',
            '--ntasks=2',  
            '--ntasks-per-node=2',  
            '--cpus-per-task=1'
        ]

