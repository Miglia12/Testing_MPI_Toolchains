import reframe as rfm
import reframe.utility.sanity as sn
import json

@rfm.simple_test
class PutLatencyTest(rfm.RunOnlyRegressionTest):
    valid_systems = ['aion:batch']  # This must match the system and partition name in the config file
    valid_prog_environs = ['gnu']   # This must match the desired environment in the config file
    num_tasks = 2                   # Set the tasks
    num_tasks_per_node = 2        

    def __init__(self):
        super().__init__()
        with open('paths.json', 'r') as file: # Loads the json file created by the batch script
            config = json.load(file)            
        self.executable = config['put_latency'] # Gets the executable path from the json
        self.executable_opts = []   # If the exectuables needs some options

    @run_before('run')
    def set_computational_resources(self):
        self.job.options = [
            '--time=00:05:00',
            '--nodes=1',
            '--ntasks=2',  
            '--ntasks-per-node=2',  
            '--cpus-per-task=1'
        ]

    @sanity_function
    def validate(self):
        return sn.assert_found(r'OSU MPI_Put Latency Test', self.stdout)