from base.osu_benchmarks_base import OSU_Micro_Benchmark

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class PutLatencyTest(OSU_Micro_Benchmark):
    
    def __init__(self):
        super().__init__()           
        self.executable = self.paths['put_latency'] # Gets the executable path from the json
        self.executable_opts = []   # If the exectuables needs some options

    @sanity_function
    def validate(self):
        return sn.assert_found(r'OSU MPI_Put Latency Test', self.stdout)
