from hpctestlib.microbenchmarks.mpi.osu import osu_benchmark

import reframe as rfm
import reframe.utility.sanity as sn
import os

class fetch_osu_benchmarks(rfm.RunOnlyRegressionTest):
    valid_systems = ['aion:batch']
    valid_prog_environs = ['*']

    descr = 'Fetch OSU benchmarks'
    version = variable(str, value='7.4')
    executable = 'wget'
    executable_opts = [
        f'http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-{version}.tar.gz'  # noqa: E501
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class build_osu_benchmarks(rfm.CompileOnlyRegressionTest):
    valid_systems = ['aion:batch']
    valid_prog_environs = ['*']

    descr = 'Build OSU benchmarks'
    build_system = 'Autotools'
    build_prefix = variable(str)
    osu_benchmarks = fixture(fetch_osu_benchmarks, scope='session')

    @run_before('compile')
    def prepare_build(self):
        tarball = f'osu-micro-benchmarks-{self.osu_benchmarks.version}.tar.gz'
        self.build_prefix = tarball[:-7]  # remove .tar.gz extension

        fullpath = os.path.join(self.osu_benchmarks.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 8

    @sanity_function
    def validate_build(self):
        # If compilation fails, the test would fail in any case, so nothing to
        # further validate here.
        return True


class OSUBenchmarkTestBase(rfm.RunOnlyRegressionTest):
    '''Base class of OSU benchmarks runtime tests'''

    valid_systems = ['*']
    valid_prog_environs = ['*']
    num_tasks = 2
    num_tasks_per_node = 1
    osu_binaries = fixture(build_osu_benchmarks, scope='environment')

    # @sanity_function
    # def validate_test(self):
    #     # return sn.assert_found(r'^8', self.stdout)
    #     return True


# @rfm.simple_test
# class osu_latency_test(OSUBenchmarkTestBase):
#     descr = 'OSU latency test'

#     @run_before('run')
#     def prepare_run(self):
#         self.executable = os.path.join(
#             self.osu_binaries.stagedir,
#             self.osu_binaries.build_prefix,
#             'c', 'mpi', 'pt2pt', 'osu_latency'
#         )
#         self.executable_opts = ['-x', '100', '-i', '1000']

#     @performance_function('us')
#     def latency(self):
#         return sn.extractsingle(r'^8\s+(\S+)', self.stdout, 1, float)
