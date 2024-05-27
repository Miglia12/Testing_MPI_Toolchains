import reframe as rfm
import reframe.utility.sanity as sn
import os
import json


class fetch_osu_benchmarks(rfm.RunOnlyRegressionTest):
    """
        Defines a test to fetch OSU benchmarks
        This will not be executed as a stand-alone test, but as a dependency
    """
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
    """
        Defines a test to build OSU benchmarks
        This will not be executed as a stand-alone test, but as a dependency
    """
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


def find_repo_root():
    markers = ['.git', 'README.md']
    current_dir = os.getcwd()

    while current_dir != os.path.dirname(current_dir):
        if any(os.path.exists(os.path.join(current_dir, marker)) for marker in markers):
            return os.path.abspath(current_dir)
        current_dir = os.path.dirname(current_dir)

    return None


class OSUBenchmarkBase(rfm.RunOnlyRegressionTest):
    """
        Parent class of the actual benchmark tests
        Contains common configurations for all tests
    """
    valid_systems = ['aion:batch']
    valid_prog_environs = ['*']
    descr = 'Run OSU benchmarks'
    osu_benchmarks = fixture(build_osu_benchmarks, scope='environment')

    # Define the path to get the specific test config file
    repo_root = find_repo_root()
    config_path = os.path.join(repo_root, 'configs', 'tests')
    test_type = ''
    test_name = ''

    @run_after('init')
    def load_test_config(self):
        """
            Loads the test configuration from the configs/tests JSON file based on the test type and name.
        """
        config_test_path = os.path.join(
           self.config_path, f'test_config_{self.test_type}.json')

        if not os.path.exists(config_test_path):
                self.logger.info(f'Current directory: {os.getcwd()}')
                raise FileNotFoundError(
                    f"Configuration file for {self.test_type} not found at {config_test_path}")

        with open(config_test_path, 'r') as configs:
            all_configs = json.load(configs)

        if self.test_name not in all_configs:
            self.logger.info(f'Current directory: {os.getcwd()}')
            raise ValueError(
                f"Test name '{self.test_name}' not found in configuration file {config_test_path}")

        self.test_config = all_configs[self.test_name]

    # Default: intra-node and inter-node running
    number_of_nodes_to_test = parameter([1, 2])

    @run_after('init')
    def set_computational_resources(self):
        """
            Set the computational resources (number of nodes and tasks) for the test.
        """
        self.num_nodes = self.number_of_nodes_to_test
        self.num_tasks = self.test_config['num_tasks']
        self.number_of_tasks_per_node = self.num_tasks / self.num_nodes

    @run_before('run')
    def set_test_config(self):
        """
            Set the test configuration before running the benchmark.
        """
        self.executable = os.path.join(
            self.osu_benchmarks.stagedir,
            *self.test_config['path_elements']
        )
        self.time_limit = self.test_config['time']

    @run_before('performance')
    def set_performance_reference(self):
        """
            Set the performance reference values based on the configuration.
        """
        if 'reference' not in self.test_config:
            self.reference = {}
            return
        self.reference = {
            'aion': {
                # set the reference value according to the number of tasks
                'last': tuple(self.test_config['reference'][str(self.current_environ)])
            }
        }
