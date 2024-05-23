from base.osu_base import OSUBenchmarkBase
from os import path

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class test_init(OSUBenchmarkBase):
    @run_before('run')
    def set_executable(self):
        self.executable = path.join(
            self.osu_benchmarks.stagedir,
            'osu-micro-benchmarks-7.4',
            'c',
            'mpi',
            'startup',
            'osu_init'
        )

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Init Test', self.stdout)
    

@rfm.simple_test
class test_hello(OSUBenchmarkBase):
    @run_before('run')
    def set_executable(self):
        self.executable = path.join(
            self.osu_benchmarks.stagedir,
            'osu-micro-benchmarks-7.4',
            'c',
            'mpi',
            'startup',
            'osu_hello'
        )

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Hello World Test', self.stdout)