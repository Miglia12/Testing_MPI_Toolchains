from base.osu_benchmarks_base import OSU_Micro_Benchmark

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class OsuInitTest(OSU_Micro_Benchmark):

    def __init__(self):
        super().__init__()           
        self.executable = self.paths['init']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'OSU MPI Init Test', self.stdout)
    

@rfm.simple_test
class OsuHelloTest(OSU_Micro_Benchmark):

    def __init__(self):
        super().__init__()
        self.executable = self.paths['hello']

    @sanity_function
    def validate(self):
        return sn.assert_found(r'OSU MPI Hello World Test', self.stdout)