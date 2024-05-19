import reframe as rfm
import reframe.utility.sanity as sn
import os
from pathlib import Path
import shutil

def find_repo_root(starting_dir=None, marker_files=None):

    if starting_dir is None:
        starting_dir = Path.cwd()
    else:
        starting_dir = Path(starting_dir)

    if marker_files is None:
        marker_files = ['.git', 'README.md']

    current_dir = starting_dir

    while current_dir != current_dir.parent:
        if any((current_dir / marker).exists() for marker in marker_files):
            return current_dir
        current_dir = current_dir.parent
    
    raise FileNotFoundError("Repository root not found. None of the marker files were found.")

@rfm.simple_test
class OSUMicroBenchmarkBase(rfm.RegressionTest):
    def __init__(self):
        super().__init__()
        self.valid_systems = ['aion:batch']
        self.valid_prog_environs = ['gnu']
        self.num_tasks = 2
        self.num_tasks_per_node = 2
        
        # Find the root of the repository
        repo_root = find_repo_root()

        # Paths relative to the repository root
        self.tar_file = repo_root / 'src/osu-micro-benchmarks-7.4.tar.gz'
        self.src_dir = repo_root / 'src/osu-micro-benchmarks-7.4'
        
        # Module to load
        self.modules = ['toolchain/foss/2020b']
        
        self.executable = str(self.src_dir / 'bin/osu_mbw_mr')
        self.sanity_patterns = sn.assert_found('osu_mbw_mr', self.executable)

    @run_before('compile')
    def print_working_directory(self):
        print(f"Working directory: {os.getcwd()}")

    @run_before('compile')
    def prepare_directories_and_files(self):
        # Ensure the src directory exists and extract the tar file into it
        if not self.src_dir.exists():
            os.makedirs(self.src_dir, exist_ok=True)
            os.system(f'tar -xzf {self.tar_file} -C {self.src_dir} --strip-components=1')

    @sanity_function
    def assert_installation_successful(self):
        return sn.assert_true(os.path.exists(self.executable))
