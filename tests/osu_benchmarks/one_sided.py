from base.osu_base import OSUBenchmarkBase
from os import path

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class TestPutLatency(OSUBenchmarkBase):

    test_type = 'one-sided'
    test_name = 'osu_put_latency'

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_tasks != 2,
                     'Invalid parameter combination - requires exaclty two processes')

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI_Put Latency Test', self.stdout)

    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestGetLatency(OSUBenchmarkBase):

    test_type = 'one-sided'
    test_name = 'osu_get_latency'

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_tasks != 2,
                     'Invalid parameter combination - requires exaclty two processes')

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI_Get latency Test', self.stdout)

    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestPutBW(OSUBenchmarkBase):

    test_type = 'one-sided'
    test_name = 'osu_put_bw'

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_tasks != 2,
                     'Invalid parameter combination - requires exactly two processes')

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI_Put Bandwidth Test', self.stdout)

    @performance_function('MB/s', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestGetBW(OSUBenchmarkBase):

    test_type = 'one-sided'
    test_name = 'osu_get_bw'

    @run_after('init')
    def skip_invalid(self):
        self.skip_if(self.num_tasks != 2,
                     'Invalid parameter combination - requires exactly two processes')

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI_Get Bandwidth Test', self.stdout)

    @performance_function('MB/s', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)
