# Testing_MPI_Toolchains

The goal of this project is to validate the MPI toolchains installed on the Uni.lu HPC platform. The ReFrame framework will be used to orchestrate sets of regression and sanity tests. We will leverage two sets of tests: the  [OSU benchmarking suite](http://mvapich.cse.ohio-state.edu/benchmarks/), and [Supermagic](https://github.com/hpc/supermagic).

## Folder structure
```
Testing_MPI_Toolchains/
├── configs/                    
│   ├── aion_config.py      # ReFrame configuration file
│   ├── tests/              # Test-specific configuration files
├── tests/
│   ├── osu_benchmarks/     # OSU Benchmark tests
│   │   ├── base/           
│   │   ├── collective.py
│   │   ├── one_sided.py
│   │   ├── pt2pt.py
│   │   └── startup.py
│   └── supermagic/         # Supermagic tests
│       └── supermagic.py
└── README.md
```


## Running instructions

These tests have been tailored for UniLu's Aion cluster. All necessary
configuration has already been specified in the repository files. 
To run the tests, execute the following commands from the repository's root directory:

1. Login to Aion and request access to an interactive node:
   ```bash
   si -N 2
   ```

2. Set up the environment:

```bash
module use /work/projects/mhpc-softenv/easybuild/aion-epyc-prod-2023a/modules/all/
module load devel/ReFrame
```

The first of them makes sure that the 2023 toolchain is available, as by default
only the 2020 one is available to Lmod. 

The second command loads the ReFrame module.

3. Run the specific benchmark tests using ReFrame with the `aion_config.py` configuration file:

* run the OSU Benchmark tests:
```bash
reframe -C configs/aion_config.py -c tests/osu_benchmarks --run
```

* run the Supermagic tests:
```bash
reframe -C configs/aion_config.py -c tests/supermagic --run
```

## Configuring tests

