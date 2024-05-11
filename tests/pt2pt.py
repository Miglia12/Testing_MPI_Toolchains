from base.osu_benchmarks_base import OSU_Micro_Benchmark

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class LatencyTest(OSU_Micro_Benchmark):
    
    def __init__(self):
        super().__init__()           
        self.executable = self.paths['latency'] 

    @sanity_function
    def validate(self):
        return sn.assert_found(r'OSU MPI Latency Test', self.stdout)
    

@rfm.simple_test
class BandwidthTest(OSU_Micro_Benchmark):
    
    def __init__(self):
        super().__init__()           
        self.executable = self.paths['bw']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'OSU MPI Bandwidth Test', self.stdout)