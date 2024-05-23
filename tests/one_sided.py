from base.osu_base import OSUBenchmarkBase
from os import path

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class test_put_latency(OSUBenchmarkBase):

    test_type = 'one-sided'
    test_name = 'osu_put_latency'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI_Put Latency Test', self.stdout)
