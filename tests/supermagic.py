import reframe                as rfm
import reframe.utility.sanity as sn
import os
import json


NUM_NODES          = 2
NUM_TASKS_PER_NODE = 1
TIME_LIMIT         = 5


class FetchStep(rfm.RunOnlyRegressionTest):
    valid_systems       = ['aion:batch']
    valid_prog_environs = [         '*']
    descr               = 'Fetch SuperMagic benchmarks'
    local               = True
    executable          = 'wget'
    executable_opts = [
        'https://github.com/hpc/supermagic/archive/refs/heads/master.zip'
    ]

    @sanity_function
    def validate_download(self):
        return sn.assert_eq(self.job.exitcode, 0)


class BuildStep(rfm.CompileOnlyRegressionTest):
    valid_systems       = ['aion:batch']
    valid_prog_environs = [         '*']
    descr               = 'Build SuperMagic benchmarks'
    build_system        = 'Autotools'
    build_dirname       = variable(str)
    fetch_step          = fixture(FetchStep, scope='session')


    @run_before('compile')
    def prepare_build(self):
        self.build_dirname = 'supermagic-master'
        zipfile            = 'master.zip'
        fullpath           = os.path.join(self.fetch_step.stagedir, zipfile)
        self.prebuild_cmds = [
            f'cp    {fullpath} {self.stagedir}',
            f'unzip {zipfile}',
            f'cd    {self.build_dirname}',
            f'./autogen']
        self.execpath      = os.path.join(
            self.stagedir, self.build_dirname, 'supermagic')
        self.build_system.max_concurrency = 8
    
    @sanity_function
    def validate_build(self):
        return True


@rfm.simple_test
class SuperMagicTestSuite(rfm.RunOnlyRegressionTest):
    valid_systems       = ['aion:batch']
    valid_prog_environs = [         '*']
    descr               = 'Run SuperMagic benchmarks'
    build_step          = fixture(BuildStep, scope='environment')

    @run_before('run')
    def set_computational_resources(self):
        self.num_nodes          = NUM_NODES
        self.num_tasks_per_node = NUM_TASKS_PER_NODE
        self.num_tasks          = NUM_NODES * NUM_TASKS_PER_NODE

    @run_before('run')
    def set_test_config(self):
        opt_num_nodes = '-np %d' % NUM_NODES
        opt_execpath  = self.build_step.execpath

        self.executable      = 'mpirun'
        self.executable_opts = [opt_num_nodes, opt_execpath]
        self.time_limit      = TIME_LIMIT

    @sanity_function
    def validate_run(self):
        return sn.assert_found('<results> PASSED', self.stdout)
