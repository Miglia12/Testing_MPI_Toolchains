from base.osu_base import OSUBenchmarkBase

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class test_latency(OSUBenchmarkBase):

    test_type = 'pt2pt'
    test_name = 'osu_latency'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Latency Test', self.stdout)
    
    @performance_function('us', perf_key='last')
    def extract_latency(self):
        return sn.extractsingle(r'^4194304\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class test_bandwidth(OSUBenchmarkBase):
    
    test_type = 'pt2pt'
    test_name = 'osu_bw'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Bandwidth Test', self.stdout)

    @performance_function('MB/s', perf_key='last')
    def extract_bandwidth(self):
        return sn.extractsingle(r'^4194304\s+(\S+)', self.stdout, 1, float)
