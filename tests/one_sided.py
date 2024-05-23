from base.osu_base import OSUBenchmarkBase
from os import path

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class test_put_latency(OSUBenchmarkBase):

    @run_before('run')
    def set_executable(self):
        self.executable = path.join(
            self.osu_benchmarks.stagedir,
            'osu-micro-benchmarks-7.4',
            'c',
            'mpi',
            'one-sided',
            'osu_put_latency'
        )

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI_Put Latency Test', self.stdout)
