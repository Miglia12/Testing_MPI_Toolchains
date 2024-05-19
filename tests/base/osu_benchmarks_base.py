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
        self.valid_prog_environs = ['foss2020b']
        self.num_tasks = 2
        self.num_tasks_per_node = 2
        
        # Find the root of the repository
        repo_root = find_repo_root()

        # Paths relative to the repository root
        self.tar_file = repo_root / 'src/osu-micro-benchmarks-7.4.tar.gz'
        self.src_dir = repo_root / 'src/osu-micro-benchmarks-7.4'
        self.build_dir = repo_root / 'src/build_foss2020b'
        self.install_dir = repo_root / 'osu_foss2020b'
        
        # Module to load
        self.modules = ['toolchain/foss/2020b']
        
        self.executable = str(self.src_dir / 'bin/osu_mbw_mr')
        self.sanity_patterns = sn.assert_found('osu_mbw_mr', self.executable)

    @run_before('compile')
    def check_loaded_modules(self):
        # Print the loaded modules for debugging
        print("Loaded modules:")
        os.system('module list')

    @run_before('compile')
    def prepare_directories(self):
        def ensure_dir_empty(dir_path):
            if dir_path.exists():
                shutil.rmtree(dir_path)
            dir_path.mkdir(parents=True, exist_ok=True)
        
        ensure_dir_empty(self.src_dir)
        ensure_dir_empty(self.build_dir)
        ensure_dir_empty(self.install_dir)

        os.system(f'tar -xzf {self.tar_file} -C {self.src_dir} --strip-components=1')

    @sanity_function
    def assert_installation_successful(self):
        return sn.assert_true(os.path.exists(self.executable))
