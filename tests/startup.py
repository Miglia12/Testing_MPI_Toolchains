from base.osu_base import OSUBenchmarkBase

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class TestInit(OSUBenchmarkBase):

    test_type = 'startup'
    test_name = 'osu_init'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Init Test', self.stdout)


@rfm.simple_test
class TestHello(OSUBenchmarkBase):
    test_type = 'startup'
    test_name = 'osu_hello'

    @sanity_function
    def validate_run(self):
        return sn.assert_found('OSU MPI Hello World Test', self.stdout)
