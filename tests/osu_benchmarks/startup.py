from base.osu_base import OSUBenchmarkBase

import reframe as rfm
import reframe.utility.sanity as sn


@rfm.simple_test
class TestInit(OSUBenchmarkBase):

    test_type = 'startup'
    test_name = 'osu_init'

    @sanity_function
    def validate_run(self):
        # Check for the presence of the 'OSU MPI Init Test' string
        osu_test_found = sn.assert_found('OSU MPI Init Test', self.stdout)
        
        # Check for the number of tasks
        ntasks_found = sn.assert_found(f'nprocs: {self.num_tasks}', self.stdout)
        
        return osu_test_found & ntasks_found
    

@rfm.simple_test
class TestHello(OSUBenchmarkBase):
    test_type = 'startup'
    test_name = 'osu_hello'

    @sanity_function
    def validate_run(self):
        osu_test_found = sn.assert_found('OSU MPI Hello World Test', self.stdout)

        ntasks_found = sn.assert_found(f'{self.num_tasks}', self.stdout)

        return osu_test_found & ntasks_found
