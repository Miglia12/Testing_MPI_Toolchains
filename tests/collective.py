from base.osu_base import OSUBenchmarkBase

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class TestAllToAll(OSUBenchmarkBase):

    test_type = 'collective'
    test_name = 'osu_alltoall'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI All-to-All Personalized Exchange Latency Test', self.stdout)

    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestBcast(OSUBenchmarkBase):

    test_type = 'collective'
    test_name = 'osu_bcast'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Broadcast Latency Test', self.stdout)

    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestReduce(OSUBenchmarkBase):

    test_type = 'collective'
    test_name = 'osu_reduce'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Reduce Latency Test', self.stdout)
    
    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestIalltoall(OSUBenchmarkBase):

    test_type = 'collective'
    test_name = 'osu_ialltoall'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Non-blocking All-to-All Latency Test', self.stdout)
    
    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestIbcast(OSUBenchmarkBase):

    test_type = 'collective'
    test_name = 'osu_ibcast'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Non-Blocking Broadcast Latency Test', self.stdout)

    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)


@rfm.simple_test
class TestIreduce(OSUBenchmarkBase):

    test_type = 'collective'
    test_name = 'osu_ireduce'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Non-blocking Reduce Latency Test', self.stdout)

    @performance_function('us', perf_key='last')
    def extract_performance(self):
        return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)