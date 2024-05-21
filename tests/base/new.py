import reframe as rfm
import reframe.utility.sanity as sn
import os

@rfm.simple_test
class fetch_osu_benchmarks(rfm.RunOnlyRegressionTest):
    valid_systems = ['aion:batch']
    valid_prog_environs = ['*']
    descr = 'Fetch OSU benchmarks'
    version = variable(str, value='7.4')
    executable = 'wget'
    executable_opts = [
        f'http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-{version}.tar.gz'
    ]
    local = True

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)

@rfm.simple_test
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
        self.build_prefix = tarball[:-7]
        fullpath = os.path.join(self.osu_benchmarks.stagedir, tarball)
        self.prebuild_cmds = [
            f'cp {fullpath} {self.stagedir}',
            f'tar xzf {tarball}',
            f'cd {self.build_prefix}'
        ]
        self.build_system.max_concurrency = 8

    @sanity_function
    def validate_build(self):
        return True

@rfm.simple_test
class run_osu_benchmarks(rfm.RunOnlyRegressionTest):
    valid_systems = ['aion:batch']
    valid_prog_environs = ['*']
    descr = 'Run OSU benchmarks'
    osu_benchmarks = fixture(build_osu_benchmarks, scope='environment')

    @run_before('run')
    def set_executable(self):
        self.executable = os.path.join(
            self.osu_benchmarks.stagedir,
            'osu-micro-benchmarks-7.4',
            'c',
            'mpi',
            'startup',
            'osu_hello'
        )

    @sanity_function
    def validate_run(self):
        return sn.assert_found('# OSU MPI Hello World Test', self.stdout)

    @run_after('run')
    def unload_module(self):
        modules_to_unload = self.current_environ.modules
        self.postrun_cmds = [f'module unload {module}' for module in modules_to_unload]