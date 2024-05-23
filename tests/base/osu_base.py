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
        f'http://mvapich.cse.ohio-state.edu/download/mvapich/osu-micro-benchmarks-{version}.tar.gz'
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

    
class OSUBenchmarkBase(rfm.RunOnlyRegressionTest):
    valid_systems = ['aion:batch']
    valid_prog_environs = ['*']
    descr = 'Run OSU benchmarks'
    osu_benchmarks = fixture(build_osu_benchmarks, scope='environment')

    @run_before('run')
    def set_computational_resources(self):
        self.job.options = [
            '--time=00:05:00',
            '--nodes=1',
            '--ntasks=2',  
            '--ntasks-per-node=2',  
            '--cpus-per-task=1'
        ]